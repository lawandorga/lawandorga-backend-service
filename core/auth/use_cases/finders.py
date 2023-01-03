from core.auth.models import RlcUser
from core.rlc.models import Org


def rlc_user_from_id(actor, v) -> RlcUser:
    return RlcUser.objects.get(id=v, org__id=actor.org_id)


def org_from_id(_, v) -> Org:
    return Org.objects.get(id=v)


def org_user_from_uuid(actor, v) -> RlcUser:
    return RlcUser.objects.get(org_id=actor.org_id, uuid=v)
