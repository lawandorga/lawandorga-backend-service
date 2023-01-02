import json
from typing import cast

import pytest
from django.test import Client

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.questionnaires.models import QuestionnaireTemplate
from core.seedwork.repository import RepositoryWarehouse
from core.static import PERMISSION_RECORDS_ADD_RECORD


@pytest.fixture
def template(db, org):
    template = QuestionnaireTemplate.objects.create(rlc=org, name="Test Template")
    yield template


@pytest.fixture
def folder(db, org, user):
    folder = Folder.create(name="New Folder", org_pk=org.pk)
    folder.grant_access(to=user["rlc_user"])
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    r.save(folder)
    yield r.retrieve(org.pk, folder.uuid)


def test_publish_questionnaire(user, db, template, folder):
    user["rlc_user"].grant(PERMISSION_RECORDS_ADD_RECORD)
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/questionnaires/questionnaires/v2/publish/",
        data=json.dumps({"folder": str(folder.uuid), "template": template.id}),
        content_type="application/json",
    )
    assert response.status_code == 200
