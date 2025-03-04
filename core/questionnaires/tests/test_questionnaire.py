import json

import pytest
from django.test import Client

from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.models import Org
from core.permissions.static import PERMISSION_RECORDS_ADD_RECORD
from core.questionnaires.models import Questionnaire, QuestionnaireTemplate
from core.seedwork import test_helpers
from core.seedwork import test_helpers as data


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def user(db, org):
    user_1 = data.create_org_user(rlc=org)
    org.generate_keys()
    yield user_1


@pytest.fixture
def template(db, org):
    template = QuestionnaireTemplate.objects.create(rlc=org, name="Test Template")
    yield template


@pytest.fixture
def folder(db, org, user):
    folder = Folder.create(name="New Folder", org_pk=org.pk)
    folder.grant_access(to=user["org_user"])
    r = DjangoFolderRepository()
    r.save(folder)
    yield r.retrieve(org.pk, folder.uuid)


@pytest.fixture
def raw_org():
    yield test_helpers.create_raw_org()


@pytest.fixture
def raw_user(raw_org):
    yield test_helpers.create_raw_org_user(raw_org)


@pytest.fixture
def raw_template(raw_org):
    yield QuestionnaireTemplate.create("Dummy's Template", raw_org)


@pytest.fixture
def raw_folder(raw_user):
    yield test_helpers.create_raw_folder(raw_user)


@pytest.fixture
def raw_questionnaire(raw_template, raw_user, raw_folder):
    yield Questionnaire.create(raw_template, raw_folder, raw_user)


@pytest.fixture
def raw_question(raw_template):
    yield raw_template.add_question("TEXTAREA", "How old is Mr. Dummy?")


def test_publish_questionnaire(user, db, template, folder):
    user["org_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {
                "folder_uuid": str(folder.uuid),
                "template_id": template.id,
                "action": "questionnaires/publish_questionnaire",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_answer_question(raw_user, raw_question, raw_questionnaire):
    text = "Mr. Dummy is older than the universe."
    answer = raw_questionnaire.add_answer(raw_question, text)
    assert answer.data != text
    answer.decrypt(raw_user)
    assert answer.data == text
