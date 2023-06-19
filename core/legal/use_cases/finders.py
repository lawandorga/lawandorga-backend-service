from core.legal.models.legal_requirement import LegalRequirement
from core.seedwork.use_case_layer import finder_function


@finder_function
def legal_requirement_from_id(_, v):
    return LegalRequirement.objects.get(id=v)
