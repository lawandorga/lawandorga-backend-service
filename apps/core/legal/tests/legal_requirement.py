import json

import pytest
from django.test import Client

from apps.core.models import Org
from apps.static import test_helpers

from ..models import LegalRequirement, LegalRequirementUser


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user = test_helpers.create_rlc_user(rlc=rlc)
    yield user


@pytest.fixture()
def legal_requirement_user(user):
    legal_requirement = LegalRequirement.objects.create(
        title="Test", content="Accept this please", accept_required=True
    )
    legal_requirement_user = LegalRequirementUser.objects.create(
        legal_requirement=legal_requirement, rlc_user=user["rlc_user"]
    )
    yield legal_requirement_user


def test_get_data_works(user, db, legal_requirement_user):
    c = Client()
    c.login(**user)
    response = c.get("/api/legal/legal_requirements/")
    d = response.json()
    assert (
        response.status_code == 200
        and d[0]["accepted"] is False
        and d[0]["legal_requirement"]["content"]
    )


def test_accept_legal_requirement(user, db, legal_requirement_user):
    c = Client()
    c.login(**user)

    response = c.post(
        "/api/legal/legal_requirements/{}/accept/".format(legal_requirement_user.pk),
        data=json.dumps({"accepted": True, "actor": user["rlc_user"].id}),
        content_type="application/json",
    )

    d = response.json()
    assert response.status_code == 200 and d["accepted"] is True
