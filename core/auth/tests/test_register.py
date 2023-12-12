import pytest
from django.test.client import Client

from core.auth.models.org_user import OrgUser
from core.legal.models import LegalRequirement


@pytest.fixture
def data(org):
    yield {
        "org": org.pk,
        "name": "Mr. Test",
        "email": "test@law-orga.de",
        "password1": "pass1234!!",
        "password2": "pass1234!!",
        "lrs": [],
    }


def test_register_works(org, data):
    c = Client()
    response = c.post("/auth/user/register/", data=data)
    assert response.status_code == 302
    assert OrgUser.objects.filter(user__email=data["email"]).exists()


def test_create_returns_error_message_on_different_passwords(org):
    c = Client()
    data = {
        "org": org.pk,
        "name": "Test",
        "email": "test@law-orga.de",
        "password1": "test1",
        "password2": "test2",
        "lrs": [],
    }
    response = c.post("/auth/user/register/", data=data)
    assert "password fields didn" in response.content.decode()
    assert not OrgUser.objects.filter(user__email=data["email"]).exists()


def test_everybody_can_get_to_user_create(db):
    client = Client()
    response = client.get("/auth/user/register/")
    assert response.status_code == 200


def test_with_legal_requirement_blocks(db, data):
    LegalRequirement.objects.create(title="Required", accept_required=True, content="")
    LegalRequirement.objects.create(
        title="Not required", accept_required=False, content=""
    )
    client = Client()
    response = client.post("/auth/user/register/", data=data)
    assert response.status_code == 200
    assert not OrgUser.objects.filter(user__email=data["email"]).exists()


def test_with_legal_requirement_works(db, data):
    lr_required = LegalRequirement.objects.create(
        title="Required", accept_required=True, content=""
    )
    data["accepted_legal_requirements"] = [lr_required.pk]
    LegalRequirement.objects.create(
        title="Not required", accept_required=False, content=""
    )
    client = Client()
    response = client.post(
        "/auth/user/register/", data={**data, "lrs": [lr_required.pk]}
    )
    assert response.status_code == 302
    assert OrgUser.objects.filter(user__email=data["email"]).exists()
