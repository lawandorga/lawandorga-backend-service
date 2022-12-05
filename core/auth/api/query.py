from core.auth.api import schemas
from core.legal.models import LegalRequirement
from core.rlc.models import Org
from core.seedwork.api_layer import Router

router = Router()


@router.get(url="page/register/", output_schema=schemas.OutputRegisterPage)
def query__register_page():
    data = {
        "orgs": Org.objects.all(),
        "legal_requirements": LegalRequirement.objects.filter(accept_required=True),
    }
    return data
