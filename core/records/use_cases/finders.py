from uuid import UUID
from core.auth.models.org_user import RlcUser
from core.records.models.setting import RecordsView
from core.seedwork.use_case_layer import finder_function


@finder_function
def find_view_by_uuid(__actor: RlcUser, uuid: UUID) -> RecordsView:
    return RecordsView.objects.get(uuid=uuid, user=__actor)
