import pytest
from django.test import Client

from core.legal.models.legal_requirement import LegalRequirementEvent
from core.legal.use_cases.legal_requirement import accept_legal_requirement
from core.models import Org
from core.seedwork import test_helpers

from ..models import LegalRequirement


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user = test_helpers.create_org_user(rlc=rlc)
    yield user


@pytest.fixture()
def legal_requirement(user):
    legal_requirement = LegalRequirement.objects.create(
        title="Test", content="Accept this please", accept_required=True
    )
    yield legal_requirement


def test_get_data_works(user, db, legal_requirement):
    c = Client()
    c.login(**user)
    response = c.get("/api/legal/legal_requirements/")
    d = response.json()
    assert (
        response.status_code == 200
        and d[0]["accepted_of_user"] is False
        and d[0]["content"]
    )


def test_accept_legal_requirement(user, db, legal_requirement):
    accept_legal_requirement(user["org_user"], legal_requirement.pk)
    assert LegalRequirementEvent.objects.filter(
        user=user["org_user"], legal_requirement=legal_requirement
    ).exists()
