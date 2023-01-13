from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_uuid
from core.records.models import Record, RecordTemplate
from core.records.use_cases.finders import record_from_id, template_from_id
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, use_case
from core.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)


@use_case
def change_record_name(__actor: RlcUser, name: str, record_id: int):
    record = record_from_id(__actor, record_id)
    record.set_name(name)
    record.save()


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_record_and_a_folder(
    __actor: RlcUser,
    name: str,
    template_id: int,
):
    template = template_from_id(__actor, template_id)

    folder_repository = cast(
        FolderRepository, RepositoryWarehouse.get(FolderRepository)
    )
    parent_folder = folder_repository.get_or_create_records_folder(
        __actor.org_id, __actor
    )

    if not parent_folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    folder = Folder.create(name=name, org_pk=__actor.org_id, stop_inherit=True)
    folder.grant_access(__actor)
    folder.set_parent(parent_folder, __actor)
    folder_repository.save(folder)

    return __create(__actor, name, folder, template)


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_record_within_a_folder(
    __actor: RlcUser,
    name: str,
    folder_uuid: UUID,
    template_id: int,
):
    folder = folder_from_uuid(__actor, folder_uuid)
    template = template_from_id(__actor, template_id)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    return __create(__actor, name, folder, template)


def __create(
    __actor: RlcUser, name: str, folder: Folder, template: RecordTemplate
) -> int:
    access_granted = False
    for user in list(__actor.org.users.all()):
        should_access = user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)
        has_access = folder.has_access(user)
        if should_access and not has_access:
            folder.grant_access(user, __actor)
            access_granted = True

    if access_granted:
        folder_repository = cast(
            FolderRepository, RepositoryWarehouse.get(FolderRepository)
        )
        folder_repository.save(folder)

    record = Record(template=template, name=name)
    record.set_folder(folder)
    record.generate_key(__actor)
    record.save()

    return record.id
