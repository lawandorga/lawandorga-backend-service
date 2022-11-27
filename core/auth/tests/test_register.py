import json

import pytest
from django.test.client import Client

from core.legal.models import LegalRequirement


@pytest.fixture
def data(org):
    yield {
        "org": org.pk,
        "name": "Mr. Test",
        "email": "test@law-orga.de",
        "password": "pass1234",
        "password_confirm": "pass1234",
    }


def test_register_works(org, data):
    c = Client()
    response = c.post(
        "/api/rlc_users/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200


def test_create_returns_error_message_on_different_passwords(org):
    c = Client()
    data = {
        "org": org.pk,
        "name": "Test",
        "email": "test@law-orga.de",
        "password": "test1",
        "password_confirm": "test2",
    }
    response = c.post(
        "/api/rlc_users/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 422


def test_everybody_can_post_to_user_create(db):
    client = Client()
    response = client.post(
        "/api/rlc_users/", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 422


def test_with_legal_requirement_blocks(db, data):
    LegalRequirement.objects.create(title='Required', accept_required=True, content='')
    LegalRequirement.objects.create(title='Not required', accept_required=False, content='')
    client = Client()
    response = client.post(
        "/api/rlc_users/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 400


def test_with_legal_requirement_works(db, data):
    lr_required = LegalRequirement.objects.create(title='Required', accept_required=True, content='')
    data['accepted_legal_requirements'] = [lr_required.pk]
    LegalRequirement.objects.create(title='Not required', accept_required=False, content='')
    client = Client()
    response = client.post(
        "/api/rlc_users/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
