from typing import List

from core.auth.models import OrgUser
from core.legal.api import schemas
from core.legal.models.legal_requirement import LegalRequirement
from core.legal.use_cases.legal_requirement import accept_legal_requirement
from core.seedwork.api_layer import Router

router = Router()


@router.get(output_schema=List[schemas.OutputLegalRequirement])
def api_list_legal_requirements(rlc_user: OrgUser):
    lrs = list(LegalRequirement.objects.all())
    for lr in lrs:
        lr._set_events_of_user(rlc_user)
        lr._set_accepted_of_user(rlc_user)
    return lrs


@router.post(
    url="<int:id>/accept/",
)
def api_accept_legal_requirement(
    data: schemas.InputLegalRequirementEventCreate, rlc_user: OrgUser
):
    accept_legal_requirement(rlc_user, data.id)
