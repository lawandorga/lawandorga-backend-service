from uuid import UUID

from core.auth.models import OrgUser
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.domain.repositories.item import ItemRepository
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS
from core.records.models.deletion import RecordsDeletion
from core.records.use_cases.finders import find_deletion_by_uuid, find_record_by_uuid
from core.seedwork.use_case_layer import use_case
from messagebus.domain.collector import EventCollector

from seedwork.injector import InjectionContext


@use_case
def create_deletion_request(__actor: OrgUser, explanation: str, record_uuid: UUID):
    record = find_record_by_uuid(__actor, record_uuid)

    deletion = RecordsDeletion.create(
        record=record, user=__actor, explanation=explanation
    )
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def accept_deletion_request(
    __actor: OrgUser,
    delete_uuid: UUID,
    r: FolderRepository,
    context: InjectionContext,
    collector: EventCollector,
):
    deletion = find_deletion_by_uuid(__actor, delete_uuid)

    repositories: list[ItemRepository] = []
    for repo in context.injections.values():
        if isinstance(repo, ItemRepository):
            repositories.append(repo)

    if deletion.record:
        record = deletion.record
        folder = r.retrieve(__actor.org_id, record.folder_uuid)
        record.delete(collector)
        r.delete(folder, repositories)
        deletion.record = None

    deletion.accept(__actor)
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def decline_deletion_request(__actor: OrgUser, delete_uuid: UUID):
    deletion = find_deletion_by_uuid(__actor, delete_uuid)

    deletion.decline(__actor)
    deletion.save()
