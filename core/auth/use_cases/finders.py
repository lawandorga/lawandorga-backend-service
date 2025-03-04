from core.auth.models import OrgUser
from core.org.models import Org
from core.seedwork.use_case_layer import finder_function


@finder_function
def org_user_from_id(actor: OrgUser, v: int) -> OrgUser:
    return OrgUser.objects.get(id=v, org__id=actor.org_id)


@finder_function
def org_from_id_dangerous(_: None, v: int) -> Org:
    return Org.objects.get(id=v)


@finder_function
def org_user_from_id_dangerous(actor: None, v: int) -> OrgUser:
    return OrgUser.objects.get(pk=v)
