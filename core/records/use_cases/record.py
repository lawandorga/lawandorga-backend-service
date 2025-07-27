from typing import Optional
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
from core.seedwork.use_case_layer import UseCaseError, UseCaseInputError, use_case
from messagebus.domain.collector import EventCollector


@use_case(permissions=[PERMISSION_RECORDS_ADD_RECORD])
def create_record_and_folder(
    __actor: OrgUser,
    token: str,
    parent_folder_uuid: Optional[UUID],
    r: FolderRepository,
    collector: EventCollector,
):
    if parent_folder_uuid:
        parent_folder = r.retrieve(__actor.org_id, parent_folder_uuid)
    else:
        parent_folder = r.get_or_create_records_folder(__actor.org_id, __actor)

    if not parent_folder.has_access(__actor):
        raise UseCaseError(
            "You can not create a record in this folder, "
            "because you have no access to this folder."
        )

    inheritance_stop = __actor.org.new_records_have_inheritance_stop

    folder = Folder.create(
        name=token, org_pk=__actor.org_id, stop_inherit=inheritance_stop
    )
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

    record = RecordsRecord.create(token, __actor, folder, collector)
    record.save()

    return folder.uuid


@use_case
def change_record_token(
    __actor: OrgUser,
    uuid: UUID,
    token: str,
    r: FolderRepository,
    collector: EventCollector,
):
    if token == "":
        raise UseCaseInputError({"token": ["The Token can not be empty."]})
    record = find_record_by_uuid(__actor, uuid)
    record.change_token(token, collector)

    folder = r.retrieve(__actor.org_id, record.folder_uuid)
    folder.update_information(name=token, force=True)

    with transaction.atomic():
        r.save(folder)
        record.save()
