from core.auth.models import RlcUser
from core.data_sheets.models import RecordDeletion
from core.data_sheets.use_cases.finders import deletion_from_id, record_from_id
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS
from core.seedwork.use_case_layer import use_case


@use_case
def create_deletion_request(__actor: RlcUser, explanation: str, record_id: int):
    record = record_from_id(__actor, record_id)

    deletion = RecordDeletion(
        requestor=__actor, state="re", record=record, explanation=explanation
    )
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def accept_deletion_request(__actor: RlcUser, deletion_id: int):
    deletion = deletion_from_id(__actor, deletion_id)

    deletion.accept(__actor)
    deletion.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS])
def decline_deletion_request(__actor: RlcUser, deletion_id: int):
    deletion = deletion_from_id(__actor, deletion_id)

    deletion.decline(__actor)
    deletion.save()
