from typing import List

from apps.core.auth.models import RlcUser
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

from . import schemas
from ..use_cases.legal_requirement import accept_legal_requirement

router = Router()


# get legal requirement
LIST_SUCCESS = "User {} has requested all legal requirements."


@router.get(output_schema=List[schemas.OutputLegalRequirementUser])
def api_list_legal_requirements(rlc_user: RlcUser):
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
    url="<int:id>/accept/",
    input_schema=schemas.InputLegalRequirementEventCreate,
    output_schema=schemas.OutputLegalRequirementUser,
)
def api_accept_legal_requirement(
    data: schemas.InputLegalRequirementEventCreate, rlc_user: RlcUser
):
    event = accept_legal_requirement(data.id, __actor=rlc_user)
    return ServiceResult(ADD_EVENT_SUCCESS, event.legal_requirement_user)
