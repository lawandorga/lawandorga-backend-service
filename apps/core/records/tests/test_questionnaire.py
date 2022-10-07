import json

import pytest
from django.test import Client

from apps.core.models import Org
from apps.recordmanagement.models import QuestionnaireTemplate
from apps.static import test_helpers as data

from ...fixtures import create_permissions
from ...static import PERMISSION_RECORDS_ADD_RECORD


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def user(db, org):
    user_1 = data.create_rlc_user(rlc=org)
    org.generate_keys()
    create_permissions()
    yield user_1


@pytest.fixture
def template(db, org):
    template = QuestionnaireTemplate.objects.create(rlc=org, name="Test Template")
    yield template


@pytest.fixture
def record(db, org, user):
    template = data.create_record_template(org)
    record = data.create_record(template["template"], [user["user"]])
    yield record["record"]


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
