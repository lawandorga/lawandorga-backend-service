from core.auth.models import RlcUser
from core.legal.models import LegalRequirementEvent
from core.legal.use_cases.finders import legal_requirement_user_from_id
from core.seedwork.use_case_layer import use_case


@use_case()
def accept_legal_requirement(
    __actor: RlcUser, legal_requirement_user_id: int
) -> LegalRequirementEvent:
    legal_requirement_user = legal_requirement_user_from_id(
        __actor, legal_requirement_user_id
    )

    event = LegalRequirementEvent(
        legal_requirement_user=legal_requirement_user,
        accepted=True,
        actor_id=__actor.id,
    )
    event.save()
    return event
