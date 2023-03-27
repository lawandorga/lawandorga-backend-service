from typing import cast
from uuid import UUID

from core.auth.models import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.records.models.deletion import RecordsDeletion
from core.records.use_cases.finders import find_deletion_by_uuid, find_record_by_uuid
from core.seedwork.repository import RepositoryWarehouse
from core.seedwork.use_case_layer import use_case
from core.static import PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS


@use_case
def create_deletion_request(__actor: RlcUser, explanation: str, record_uuid: UUID):
    record = find_record_by_uuid(__actor, record_uuid)

    deletion = RecordsDeletion.create(
        record=record, user=__actor, explanation=explanation
    )
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def accept_deletion_request(__actor: RlcUser, delete_uuid: UUID):
    deletion = find_deletion_by_uuid(__actor, delete_uuid)

    if deletion.record:
        record = deletion.record
        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
        folder = r.retrieve(__actor.org_id, record.folder_uuid)
        record.delete()
        r.delete(folder)
        deletion.record = None

    deletion.accept(__actor)
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def decline_deletion_request(__actor: RlcUser, delete_uuid: UUID):
    deletion = find_deletion_by_uuid(__actor, delete_uuid)

    deletion.decline(__actor)
    deletion.save()
