from core.auth.models.org_user import RlcUser
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES
from core.questionnaires.models.template import QuestionnaireTemplate
from core.questionnaires.use_cases.finders import questionnaire_template_from_id
from core.seedwork.use_case_layer import use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def create_questionnaire_template(__actor: RlcUser, name: str, notes: str):
    template = QuestionnaireTemplate.create(name=name, org=__actor.org, notes=notes)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def update_questionnaire_template(
    __actor: RlcUser, template_id: int, name: str, notes: str
):
    template = questionnaire_template_from_id(__actor, template_id)
    template.update(name=name, notes=notes)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def delete_questionnaire_template(__actor: RlcUser, template_id: int):
    template = questionnaire_template_from_id(__actor, template_id)
    template.delete()
