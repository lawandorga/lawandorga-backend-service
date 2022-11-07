from core.legal.models import LegalRequirementUser


def legal_requirement_user_from_id(actor, v):
    return LegalRequirementUser.objects.get(id=v, rlc_user=actor)
