import json

import pytest
from django.test import Client

from core.questionnaires.models import QuestionnaireTemplate
from core.static import PERMISSION_RECORDS_ADD_RECORD


@pytest.fixture
def template(db, org):
    template = QuestionnaireTemplate.objects.create(rlc=org, name="Test Template")
    yield template


def test_publish_questionnaire(user, db, template, record):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/records/questionnaires/v2/publish/",
        data=json.dumps({"record": record.id, "template": template.id}),
        content_type="application/json",
    )
    assert response.status_code == 200
