from core.rlc.models import Group


def group_from_id(actor, v):
    return Group.objects.get(id=v, from_rlc__id=actor.org_id)
