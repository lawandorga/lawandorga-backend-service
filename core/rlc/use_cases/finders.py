from core.auth.models import RlcUser
from core.rlc.models import Group
from core.seedwork.use_case_layer import finder_function


@finder_function
def group_from_id(actor: RlcUser, v: int):
    return Group.objects.get(id=v, from_rlc__id=actor.org_id)
