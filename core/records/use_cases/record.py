from typing import cast
from uuid import UUID

from django.db import transaction

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.static import (
    PERMISSION_RECORDS_ACCESS_ALL_RECORDS,
    PERMISSION_RECORDS_ADD_RECORD,
)
from core.records.models.record import RecordsRecord
from core.records.use_cases.finders import find_record_by_uuid
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_record(__actor: OrgUser, token: str):
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository.IDENTIFIER))

    parent_folder = r.get_or_create_records_folder(__actor.org_id, __actor)

    if not parent_folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, "
            "because you have no access to this folder."
        )

    folder = Folder.create(name=token, org_pk=__actor.org_id, stop_inherit=True)
    folder.grant_access(__actor)

    for user in list(__actor.org.users.all()):
        should_access = user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)
        has_access = folder.has_access(user)
        if should_access and not has_access:
            folder.grant_access(user, __actor)

    # todo: grant access to all users who should have
    folder.set_parent(parent_folder, __actor)
    folder.restrict()
    r.save(folder)

    record = RecordsRecord.create(token, __actor, folder)
    record.save()

    return folder.uuid


@use_case
def change_record_token(__actor: OrgUser, uuid: UUID, token: str):
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))

    record = find_record_by_uuid(__actor, uuid)
    record.change_token(token)

    folder = r.retrieve(__actor.org_id, record.folder_uuid)
    folder.update_information(name=token, force=True)

    with transaction.atomic():
        r.save(folder)
        record.save()
