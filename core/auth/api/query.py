from django.db.models import Q

from core.auth.models import RlcUser
from core.legal.models import LegalRequirement
from core.rlc.models import Org
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get(url="page/register/", output_schema=schemas.OutputRegisterPage)
def query__register_page():
    data = {
        "orgs": Org.objects.all(),
        "legal_requirements": LegalRequirement.objects.filter(
            Q(accept_required=True) | Q(show_on_register=True)
        ),
    }
    return data


@router.get(url="page/dashboard/", output_schema=schemas.OutputDashboardPage)
def query__dashboard_page(rlc_user: RlcUser):
    return rlc_user.information
