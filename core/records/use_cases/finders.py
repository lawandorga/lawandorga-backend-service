from uuid import UUID

from django.db.models import Q

from core.auth.models.org_user import OrgUser
from core.records.models.access import RecordsAccessRequest
from core.records.models.deletion import RecordsDeletion
from core.records.models.record import RecordsRecord
from core.records.models.setting import RecordsView
from core.seedwork.use_case_layer import finder_function


@finder_function
def find_view_by_uuid(__actor: OrgUser, uuid: UUID) -> RecordsView:
    return RecordsView.objects.filter(Q(user=__actor) | Q(org_id=__actor.org_id)).get(
        uuid=uuid
    )


@finder_function
def find_record_by_uuid(__actor: OrgUser, uuid: UUID) -> RecordsRecord:
    return RecordsRecord.objects.get(uuid=uuid, org_id=__actor.org_id)


@finder_function
def find_deletion_by_uuid(actor: OrgUser, v: UUID) -> RecordsDeletion:
    return RecordsDeletion.objects.get(
        Q(uuid=v)
        & (
            Q(requestor__org_id=actor.org_id)
            | Q(processor__org_id=actor.org_id)
            | Q(record__org_id=actor.org_id)
        )
    )


@finder_function
def find_access_by_uuid(actor: OrgUser, v: UUID) -> RecordsAccessRequest:
    return RecordsAccessRequest.objects.get(
        Q(uuid=v)
        & (
            Q(requestor__org_id=actor.org_id)
            | Q(processor__org_id=actor.org_id)
            | Q(record__org_id=actor.org_id)
        )
    )
