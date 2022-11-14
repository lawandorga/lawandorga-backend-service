from core.auth.models import RlcUser


def rlc_user_from_id(actor, v):
    return RlcUser.objects.get(id=v, org__id=actor.org_id)
