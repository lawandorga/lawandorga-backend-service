from core.auth.models import RlcUser
from core.legal.models import LegalRequirementEvent, LegalRequirementUser
from core.seedwork.use_case_layer import use_case


@use_case()
def accept_legal_requirement(
    legal_requirement_user: LegalRequirementUser, __actor: RlcUser
) -> LegalRequirementEvent:
    event = LegalRequirementEvent(
        legal_requirement_user=legal_requirement_user,
        accepted=True,
        actor_id=__actor.id,
    )
    event.save()
    return event
