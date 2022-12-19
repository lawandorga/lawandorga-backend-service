from typing import Optional, cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.use_cases.finders import folder_from_uuid, rlc_user_from_slug
from core.seedwork.api_layer import ApiError
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, find, use_case
from messagebus import Event


def get_repository() -> FolderRepository:
    repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    return repository


@use_case()
def create_folder(__actor: RlcUser, name: str, parent: Optional[UUID]):
    r = get_repository()
    folder = Folder.create(name=name, org_pk=__actor.org_id)
    if parent:
        parent_folder = r.retrieve(__actor.org_id, parent)
        folder.set_parent(parent=parent_folder, by=__actor)
    else:
        folder.grant_access(to=__actor)
    r.save(folder)


@use_case
def rename_folder(__actor: RlcUser, name: str, folder=find(folder_from_uuid)):
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
    if folder.has_access(__actor):
        r.delete(folder)
    else:
        raise UseCaseError(
            "You can not delete this folder because you have no access to this folder."
        )


@use_case
def grant_access(
    __actor: RlcUser, to=find(rlc_user_from_slug), folder=find(folder_from_uuid)
):
    if not folder.has_access(__actor):
        raise ApiError("You need access to this folder in order to do that.")

    r = get_repository()
    folder.grant_access(to=to, by=__actor)
    r.save(folder)


@use_case
def revoke_access(
    __actor: RlcUser, of=find(rlc_user_from_slug), folder=find(folder_from_uuid)
):
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
def move_folder(
    __actor: RlcUser, folder=find(folder_from_uuid), target=find(folder_from_uuid)
):
    folder.move(target, __actor)
    r = get_repository()
    r.save(folder)


@use_case
def toggle_inheritance(__actor: RlcUser, folder=find(folder_from_uuid)):
    if not folder.has_access(__actor):
        raise ApiError("You need access to this folder in order to do that.")

    if folder.stop_inherit:
        folder.allow_inheritance()
    else:
        folder.stop_inheritance()
    r = get_repository()
    r.save(folder)


@use_case(event_handler=True)
def item_name_changed(event: Event):
    org_pk = event.data["org_pk"]
    item_repository = cast(
        ItemRepository, RepositoryWarehouse.get(event.data["repository"])
    )
    item = item_repository.retrieve(uuid=UUID(event.data["uuid"]), org_pk=org_pk)
    r = get_repository()
    folder = r.retrieve(org_pk=org_pk, uuid=UUID(event.data["folder_uuid"]))
    folder.update_item(item)
    r.save(folder)


@use_case(event_handler=True)
def invalidate_folder_keys(event: Event):
    org_user = RlcUser.objects.get(uuid=event.data["org_user_uuid"])
    r = get_repository()
    folders = r.get_list(org_user.org_id)
    for folder in folders:
        folder.invalidate_keys_of(org_user)
        r.save(folder)


@use_case(event_handler=True)
def correct_folder_keys(event: Event):
    of = RlcUser.objects.get(uuid=event.data["org_user_uuid"])
    by = RlcUser.objects.get(uuid=event.data["by_org_user_uuid"])
    assert of.org_id == by.org_id

    r = get_repository()
    folders = r.get_list(of.org_id)
    for f in folders:
        if f.has_access(by):
            if f.has_invalid_keys(of):
                f.fix_keys(of, by)
                r.save(f)
