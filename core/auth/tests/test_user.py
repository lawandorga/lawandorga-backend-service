import pytest
from django.conf import settings
from django.test import Client

from core.seedwork import test_helpers


@pytest.fixture
def user(db, org):
    user = test_helpers.create_rlc_user(rlc=org)
    org.generate_keys()
    yield user


@pytest.fixture
def client(user):
    c = Client()
    yield c


@pytest.fixture
def auth_client(user):
    c = Client()
    c.login(**user)
    yield c


@pytest.fixture
def login_data():
    yield {
        "email": "dummy@law-orga.de",
        "password": settings.DUMMY_USER_PASSWORD,
    }


def test_login_works(client, login_data):
    response = client.post("/login/", login_data)
    assert response.status_code == 200


def test_inactive_user_can_not_hit_the_api(user, client, login_data):
    user["rlc_user"].is_active = False
    user["rlc_user"].save(update_fields=["is_active"])
    client.login(**user)
    response = client.get("/api/rlc_users/data_self/")
    assert response.status_code == 400 and "deactivated" in response.json()["title"]


def test_login_returns_correct_email_wrong_message(client):
    data = {
        "email": "dummy@law-orga.de",
        "password": "falsch",
    }
    response = client.post("/login/", data)
    assert not response.context["user"].is_authenticated


def test_login_returns_correct_password_wrong_error(client):
    data = {
        "email": "falsch@law-orga.de",
        "password": settings.DUMMY_USER_PASSWORD,
    }
    response = client.post("/login/", data)
    assert not response.context["user"].is_authenticated


def test_everybody_can_hit_login(client):
    response = client.post("/login/")
    assert response.status_code != 401 and response.status_code != 403


def test_logout_with_not_logged_in(client):
    response = client.post("/api/logout/")
    assert response.status_code == 200


def test_logout(auth_client):
    response = auth_client.post("/api/logout/")
    assert response.status_code == 200
