from django.db.models import Q
from pydantic import BaseModel, ConfigDict

from core.auth.models import UserProfile
from core.legal.models import LegalRequirement
from core.org.models import Org
from core.seedwork.api_layer import Router

router = Router()


class OutputMatrixUser(BaseModel):
    _group: str
    matrix_id: str

    model_config = ConfigDict(from_attributes=True)


class OutputChatPage(BaseModel):
    matrix_user: OutputMatrixUser | None


@router.get(url="page/chat/", output_schema=OutputChatPage)
def query__chat_page(user: UserProfile):
    if hasattr(user, "matrix_user"):
        return {"matrix_user": user.matrix_user}
    return {"matrix_user": None}


class OutputOrg(BaseModel):
    name: str
    id: int

    model_config = ConfigDict(from_attributes=True)


class OutputLegalRequirement(BaseModel):
    title: str
    id: int
    content: str
    accept_required: bool

    model_config = ConfigDict(from_attributes=True)


class OutputRegisterPage(BaseModel):
    orgs: list[OutputOrg]
    legal_requirements: list[OutputLegalRequirement]

    model_config = ConfigDict(from_attributes=True)


@router.get(url="page/register/", output_schema=OutputRegisterPage)
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
