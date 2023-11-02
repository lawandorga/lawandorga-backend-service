from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS
from core.records.models import RecordsAccessRequest
from core.records.use_cases.finders import find_access_by_uuid, find_record_by_uuid
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import use_case


@use_case
def create_access_request(__actor: RlcUser, explanation: str, record_uuid: UUID):
    record = find_record_by_uuid(__actor, record_uuid)
    access = RecordsAccessRequest.create(record, __actor, explanation)
    access.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS])
def grant_access_request(__actor: RlcUser, access_uuid: UUID):
    access = find_access_by_uuid(__actor, access_uuid)
    record = access.record
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    folder = r.retrieve(__actor.org_id, record.folder_uuid)
    folder.grant_access(access.requestor, __actor)
    r.save(folder)
    access.grant(__actor)
    access.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS])
def decline_access_request(__actor: RlcUser, access_uuid: UUID):
    access = find_access_by_uuid(__actor, access_uuid)
    access.decline(__actor)
    access.save()
