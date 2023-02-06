from uuid import UUID

from core.auth.models import RlcUser
from core.rlc.models import Org
from core.seedwork.message_layer import MessageBusActor
from core.seedwork.use_case_layer import finder_function


@finder_function
def rlc_user_from_id(actor: RlcUser, v: int) -> RlcUser:
    return RlcUser.objects.get(id=v, org__id=actor.org_id)


@finder_function
def org_from_id_dangerous(_: None, v: int) -> Org:
    return Org.objects.get(id=v)


@finder_function
def org_user_from_uuid(actor: RlcUser | MessageBusActor, v: UUID) -> RlcUser:
    org_id: int = actor.org_id  # type: ignore
    return RlcUser.objects.get(org_id=org_id, uuid=v)


@finder_function
def org_user_from_id_dangerous(actor: None, v: int) -> RlcUser:
    return RlcUser.objects.get(pk=v)
