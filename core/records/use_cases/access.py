from uuid import UUID

from core.auth.models import OrgUser
from core.folders.domain.repositories.folder import FolderRepository
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS
from core.records.models import RecordsAccessRequest
from core.records.use_cases.finders import find_access_by_uuid, find_record_by_uuid
from core.seedwork.use_case_layer import use_case


@use_case
def create_access_request(__actor: OrgUser, explanation: str, record_uuid: UUID):
    record = find_record_by_uuid(__actor, record_uuid)
    access = RecordsAccessRequest.create(record, __actor, explanation)
    access.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS])
def grant_access_request(__actor: OrgUser, access_uuid: UUID, r: FolderRepository):
    access = find_access_by_uuid(__actor, access_uuid)
    record = access.record
    folder = r.retrieve(__actor.org_id, record.folder_uuid)
    if not folder.has_access(access.requestor):
        requestor = access.requestor
        folder.grant_access(requestor, __actor)
        requestor.keyring.store()
        r.save(folder)
    access.grant(__actor)
    access.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS])
def decline_access_request(__actor: OrgUser, access_uuid: UUID):
    access = find_access_by_uuid(__actor, access_uuid)
    access.decline(__actor)
    access.save()
