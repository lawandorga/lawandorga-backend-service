from core.auth.models import OrgUser
from core.legal.api import schemas
from core.legal.models.legal_requirement import LegalRequirement
from core.seedwork.api_layer import Router

router = Router()


@router.get(output_schema=list[schemas.OutputLegalRequirement])
def api_list_legal_requirements(org_user: OrgUser):
    lrs = list(LegalRequirement.objects.all())
    for lr in lrs:
        lr._set_events_of_user(org_user)
        lr._set_accepted_of_user(org_user)
    return lrs
