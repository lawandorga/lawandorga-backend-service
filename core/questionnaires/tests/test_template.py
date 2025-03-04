from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES
from core.questionnaires.models.template import QuestionnaireTemplate
from core.questionnaires.use_cases.template import (
    create_questionnaire_template,
    delete_questionnaire_template,
    update_questionnaire_template,
)
from core.seedwork import test_helpers as helpers


def test_create_template(db):
    user = helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES)
    create_questionnaire_template(
        user, "Test Template", "A template for testing purposes."
    )
    assert QuestionnaireTemplate.objects.filter(name="Test Template").exists()


def test_update_template(db):
    user = helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES)
    template = helpers.create_questionnaire_template(user.org, save=True)
    update_questionnaire_template(user, template.id, "New Name", "New Notes")
    assert QuestionnaireTemplate.objects.filter(name="New Name").exists()


def test_delete_template(db):
    user = helpers.create_org_user()["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_RECORD_QUESTIONNAIRES)
    template = helpers.create_questionnaire_template(user.org, save=True)
    delete_questionnaire_template(user, template.id)
    assert not QuestionnaireTemplate.objects.filter(id=template.id).exists()
