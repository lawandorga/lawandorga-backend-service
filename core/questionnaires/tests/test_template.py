from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES
from core.questionnaires.models.template import QuestionnaireTemplate
from core.questionnaires.use_cases.template import create_questionnaire_template
from core.seedwork import test_helpers as helpers


def test_create_template(db):
    user = helpers.create_rlc_user()["rlc_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES)
    create_questionnaire_template(
        user, "Test Template", "A template for testing purposes."
    )
    assert QuestionnaireTemplate.objects.filter(name="Test Template").exists()
