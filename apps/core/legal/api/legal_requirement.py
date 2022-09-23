from typing import List

from apps.core.auth.models import RlcUser
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

from ..models import LegalRequirementEvent, LegalRequirementUser
from . import schemas

router = Router()


# get legal requirement
LIST_SUCCESS = "User {} has requested all legal requirements."


@router.get(output_schema=List[schemas.LegalRequirementUser], auth=True)
def list_legal_requirements(rlc_user: RlcUser):
    legal_requirements = list(rlc_user.legal_requirements_user.all())
    return ServiceResult(LIST_SUCCESS, legal_requirements)


# add event
ADD_EVENT_SUCCESS = "User {} created a new legal requirement event."
ADD_EVENT_ERROR_ACCEPTED = (
    "User {} tried to add an event, but the legal requirement was already accepted."
)
ADD_EVENT_ERROR_NOT_FOUND = (
    "User {} tried to add an event, but no legal requirement was found."
)


@router.post(
    url="<int:id>/add_event/",
    input_schema=schemas.LegalRequirementEventCreate,
    output_schema=schemas.LegalRequirementEvent,
    auth=True,
)
def create_legal_requirement_event(
    data: schemas.LegalRequirementEventCreate, rlc_user: RlcUser
):
    legal_requirement_user = LegalRequirementUser.objects.filter(id=data.id).first()
    if legal_requirement_user is None:
        return ServiceResult(
            ADD_EVENT_ERROR_NOT_FOUND,
            error="The event could not be added because it is unknown where to add it to.",
        )

    event = LegalRequirementEvent(
        legal_requirement_user=legal_requirement_user,
        accepted=data.accepted,
        actor_id=data.actor,
    )
    event.save()
    return ServiceResult(ADD_EVENT_SUCCESS, event)
