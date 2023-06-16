from core.auth.models import RlcUser
from core.rlc.models import Group, Note
from core.seedwork.use_case_layer import finder_function


@finder_function
def group_from_id(actor: RlcUser, v: int) -> Group:
    return Group.objects.get(id=v, from_rlc__id=actor.org_id)


@finder_function
def note_from_id(actor: RlcUser, v: int) -> Note:
    return Note.objects.get(id=v, rlc_id=actor.org_id)
