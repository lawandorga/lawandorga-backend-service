import json

from django.test.client import Client


def test_register_works(org):
    c = Client()
    data = {
        "org": org.pk,
        "name": "Mr. Test",
        "email": "test@law-orga.de",
        "password": "pass1234",
        "password_confirm": "pass1234",
    }
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
