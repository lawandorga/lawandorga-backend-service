from uuid import UUID

from core.auth.models import OrgUser
from core.data_sheets.models import DataSheet, DataSheetTemplate
from core.data_sheets.use_cases.finders import (
    sheet_from_id,
    sheet_from_uuid,
    template_from_id,
)
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_uuid
from core.permissions.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def change_sheet_name(__actor: OrgUser, name: str, record_id: int):
    sheet = sheet_from_id(__actor, record_id)
    sheet.set_name(name)
    sheet.save()


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_data_sheet_and_folder(
    __actor: OrgUser,
    name: str,
    template_id: int,
    folder_repository: FolderRepository,
) -> DataSheet:
    template = template_from_id(__actor, template_id)

    parent_folder = folder_repository.get_or_create_records_folder(
        __actor.org_id, __actor
    )

    if not parent_folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    inheritance_stop = __actor.org.new_records_have_inheritance_stop

    folder = Folder.create(
        name=name, org_pk=__actor.org_id, stop_inherit=inheritance_stop
    )
    folder.grant_access(__actor)
    folder.set_parent(parent_folder, __actor)
    folder_repository.save(folder)

    return __create(__actor, name, folder, template, folder_repository)


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_a_data_sheet_within_a_folder(
    __actor: OrgUser,
    name: str,
    folder_uuid: UUID,
    template_id: int,
    r: FolderRepository,
) -> DataSheet:
    folder = folder_from_uuid(__actor, folder_uuid)
    template = template_from_id(__actor, template_id)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, because you have no access to this folder."
        )

    return __create(__actor, name, folder, template, r)


def __create(
    __actor: OrgUser,
    name: str,
    folder: Folder,
    template: DataSheetTemplate,
    folder_repository: FolderRepository,
) -> DataSheet:
    access_granted = False
    for user in list(__actor.org.users.all()):
        should_access = user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)
        has_access = folder.has_access(user)
        if should_access and not has_access:
            folder.grant_access(user, __actor)
            access_granted = True

    if access_granted:
        folder_repository.save(folder)

    sheet = DataSheet(template=template, name=name)
    sheet.set_folder(folder)
    sheet.generate_key(__actor)
    sheet.save()

    return sheet


@use_case(permissions=[PERMISSION_RECORDS_ACCESS_ALL_RECORDS])
def delete_data_sheet(__actor: OrgUser, sheet_uuid: UUID):
    record = sheet_from_uuid(__actor, sheet_uuid)
    record.delete()
