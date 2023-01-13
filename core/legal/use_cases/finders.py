from core.legal.models import LegalRequirementUser
from core.seedwork.use_case_layer import finder_function


@finder_function
def legal_requirement_user_from_id(actor, v):
    return LegalRequirementUser.objects.get(id=v, rlc_user=actor)
