from core.auth.models.org_user import RlcUser
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES
from core.questionnaires.models.template import QuestionnaireTemplate
from core.seedwork.use_case_layer import use_case


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES])
def create_questionnaire_template(__actor: RlcUser, name: str, notes: str):
    template = QuestionnaireTemplate.create(name=name, org=__actor.org, notes=notes)
    template.save()
