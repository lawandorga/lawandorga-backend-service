from pydantic import BaseModel

from core.auth.models.org_user import RlcUser
from core.questionnaires.use_cases.template import create_questionnaire_template
from core.seedwork.api_layer import Router

router = Router()


class InputTemplateCreate(BaseModel):
    name: str
    notes: str


@router.post()
def command__create_template(data: InputTemplateCreate, rlc_user: RlcUser):
    create_questionnaire_template(rlc_user, name=data.name, notes=data.notes)
