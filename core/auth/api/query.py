from django.db.models import Q

from core.auth.models import RlcUser, UserProfile
from core.legal.models import LegalRequirement
from core.rlc.models import Org
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get(url="page/chat/", output_schema=schemas.OutputChatPage)
def query__chat_page(user: UserProfile):
    if hasattr(user, "matrix_user"):
        return {"matrix_user": user.matrix_user}
    return {"matrix_user": None}


@router.get(url="page/register/", output_schema=schemas.OutputRegisterPage)
def query__register_page():
    data = {
        "orgs": list(Org.objects.all()),
        "legal_requirements": list(
            LegalRequirement.objects.filter(
                Q(accept_required=True) | Q(show_on_register=True)
            )
        ),
    }
    return data


@router.get(url="page/dashboard/", output_schema=schemas.OutputDashboardPage)
def query__dashboard_page(rlc_user: RlcUser):
    return rlc_user.information
