from typing import Optional, cast
from uuid import UUID

from core.auth.models import RlcUser
from core.auth.use_cases.finders import org_user_from_uuid
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.use_cases.finders import (
    folder_from_uuid,
    item_from_repository_and_uuid,
    rlc_user_from_uuid,
)
from core.seedwork.api_layer import ApiError
from core.seedwork.message_layer import MessageBusActor
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, check_permissions, use_case
from core.static import PERMISSION_FOLDERS_TOGGLE_INHERITANCE


def get_repository() -> FolderRepository:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    return repository


@use_case()
def create_folder(__actor: RlcUser, name: str, parent: Optional[UUID]):
    r = get_repository()
    folder = Folder.create(name=name, org_pk=__actor.org_id)
    folder.grant_access(to=__actor)
    if parent:
        parent_folder = r.retrieve(__actor.org_id, parent)
        folder.set_parent(parent=parent_folder, by=__actor)
    r.save(folder)


@use_case
def rename_folder(__actor: RlcUser, name: str, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)
    r = get_repository()
    folder.update_information(name=name)
    r.save(folder)


@use_case()
def update_folder(__actor: RlcUser, folder_pk: UUID, name: str):
    r = get_repository()
    folder = r.retrieve(org_pk=__actor.org_id, uuid=folder_pk)
    folder.update_information(name=name)
    r.save(folder)


@use_case()
def delete_folder(__actor: RlcUser, folder_pk: UUID):
    r = get_repository()
    folder = r.retrieve(org_pk=__actor.org_id, uuid=folder_pk)

    for f in r.get_list(__actor.org_id):
        if f.parent_uuid == folder.uuid:
            raise UseCaseError(
                "You can not delete this folder because it has subfolders. Delete the subfolders first."
            )

    if "RECORD" in map(lambda i: i.repository, folder.items):
        raise UseCaseError(
            "You can not delete this folder because it contains a record. Delete the record first."
        )

    if folder.has_access(__actor):
        r.delete(folder)
    else:
        raise UseCaseError(
            "You can not delete this folder because you have no access to this folder."
        )


@use_case
def grant_access(__actor: RlcUser, to_uuid: UUID, folder_uuid: UUID):
    to = rlc_user_from_uuid(__actor, to_uuid)
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        raise ApiError("You need access to this folder in order to do that.")

    r = get_repository()
    folder.grant_access(to=to, by=__actor)
    r.save(folder)


@use_case
def revoke_access(__actor: RlcUser, of_uuid: UUID, folder_uuid: UUID):
    of = rlc_user_from_uuid(__actor, of_uuid)
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        raise ApiError("You need access to this folder in order to do that.")

    r = get_repository()
    folder.revoke_access(of=of)
    r.save(folder)


@use_case
def correct_folder_keys_of_others(__actor: RlcUser):
    r = get_repository()
    folders = r.get_list(__actor.org_id)
    users = list(__actor.org.users.exclude(pk=__actor.pk))
    for f in folders:
        if f.has_access(__actor):
            for u in users:
                if f.has_invalid_keys(u):
                    f.fix_keys(u, __actor)
                    r.save(f)


@use_case
def move_folder(__actor: RlcUser, folder_uuid: UUID, target_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)
    target = folder_from_uuid(__actor, target_uuid)

    folder.move(target, __actor)
    r = get_repository()
    r.save(folder)


@use_case
def toggle_inheritance(__actor: RlcUser, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        check_permissions(
            __actor,
            [PERMISSION_FOLDERS_TOGGLE_INHERITANCE],
            message_addition="Or access to this folder.",
        )

    if folder.stop_inherit:
        folder.allow_inheritance()
    else:
        folder.stop_inheritance()
    r = get_repository()
    r.save(folder)


@use_case()
def rename_item_in_folder(
    __actor: MessageBusActor,
    repository_name: str,
    item_uuid: UUID,
    folder_uuid: UUID,
):
    item = item_from_repository_and_uuid(__actor.org_pk, repository_name, item_uuid)
    folder = folder_from_uuid(__actor, folder_uuid)
    r = get_repository()
    folder.update_item(item)
    r.save(folder)


@use_case
def delete_item_from_folder(__actor: MessageBusActor, uuid: UUID, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)
    r = get_repository()
    folder.remove_item(uuid)
    r.save(folder)


@use_case
def add_item_to_folder(
    __actor: MessageBusActor,
    repository_name: str,
    item_uuid: UUID,
    folder_uuid: UUID,
):
    item = item_from_repository_and_uuid(__actor.org_pk, repository_name, item_uuid)
    folder = folder_from_uuid(__actor, folder_uuid)
    r = get_repository()
    folder.add_item(item)
    r.save(folder)


@use_case
def invalidate_keys_of_user(__actor: MessageBusActor, user_uuid: UUID):
    user = org_user_from_uuid(__actor, user_uuid)
    r = get_repository()
    folders = r.get_list(user.org_id)
    for folder in folders:
        folder.invalidate_keys_of(user)
        r.save(folder)


@use_case
def correct_keys_of_user_by_user(
    __actor: MessageBusActor, of_uuid: UUID, by_uuid: UUID
):
    of = org_user_from_uuid(__actor, of_uuid)
    by = org_user_from_uuid(__actor, by_uuid)
    assert of.org_id == by.org_id

    r = get_repository()
    folders = r.get_list(of.org_id)
    for f in folders:
        if f.has_access(by):
            if f.has_invalid_keys(of):
                f.fix_keys(of, by)
                r.save(f)
