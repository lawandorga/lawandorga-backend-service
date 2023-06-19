from pydantic import BaseModel

from core.auth.models.org_user import RlcUser
from core.questionnaires.use_cases.template import (
    create_questionnaire_template,
    delete_questionnaire_template,
    update_questionnaire_template,
)
from core.seedwork.api_layer import Router

router = Router()


class InputTemplateCreate(BaseModel):
    name: str
    notes: str = ""


@router.post()
def command__create_template(data: InputTemplateCreate, rlc_user: RlcUser):
    create_questionnaire_template(rlc_user, name=data.name, notes=data.notes)


class InputTemplateUpdate(BaseModel):
    name: str
    notes: str = ""
    id: int


@router.post("<int:id>/")
def command__update_template(data: InputTemplateUpdate, rlc_user: RlcUser):
    update_questionnaire_template(
        rlc_user, template_id=data.id, name=data.name, notes=data.notes
    )


class InputTemplateDelete(BaseModel):
    id: int


@router.delete("<int:id>/")
def command__delete_template(data: InputTemplateDelete, rlc_user: RlcUser):
    delete_questionnaire_template(rlc_user, template_id=data.id)
