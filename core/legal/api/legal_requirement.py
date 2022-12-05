from typing import List

from core.auth.models import RlcUser
from core.legal.api import schemas
from core.legal.use_cases.legal_requirement import accept_legal_requirement
from core.seedwork.api_layer import Router

router = Router()


@router.get(output_schema=List[schemas.OutputLegalRequirementUser])
def api_list_legal_requirements(rlc_user: RlcUser):
    legal_requirements = list(
        rlc_user.legal_requirements_user.order_by("-legal_requirement__accept_required")
    )
    return legal_requirements


@router.post(
    url="<int:id>/accept/",
    input_schema=schemas.InputLegalRequirementEventCreate,
    output_schema=schemas.OutputLegalRequirementUser,
)
def api_accept_legal_requirement(
    data: schemas.InputLegalRequirementEventCreate, rlc_user: RlcUser
):
    event = accept_legal_requirement(rlc_user, data.id)
    return event.legal_requirement_user
