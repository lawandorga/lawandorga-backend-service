from core.auth.models import RlcUser
from core.records.models import RecordDeletion
from core.records.use_cases.finders import deletion_from_id, record_from_id
from core.seedwork.use_case_layer import find, use_case
from core.static import PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS


@use_case
def create_deletion_request(
    __actor: RlcUser, explanation: str, record=find(record_from_id)
):
    deletion = RecordDeletion(
        requestor=__actor, state="re", record=record, explanation=explanation
    )
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def accept_deletion_request(__actor: RlcUser, deletion=find(deletion_from_id)):
    deletion.accept(__actor)
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def decline_deletion_request(__actor: RlcUser, deletion=find(deletion_from_id)):
    deletion.decline(__actor)
    deletion.save()
