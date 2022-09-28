import json
from datetime import datetime, timedelta

import pytest
from django.test import Client

from apps.core.models import Org
from apps.recordmanagement.models import RecordTemplate
from apps.static import test_helpers as data

from ...fixtures import create_permissions
from ...static import PERMISSION_ADMIN_MANAGE_USERS
from ..models import RlcUser
from ..token_generator import EmailConfirmationTokenGenerator


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def rlc_user_2(db, org):
    user_2 = data.create_rlc_user(email="dummy2@law-orga.de", rlc=org)
    yield user_2


@pytest.fixture
def user(db, rlc_user_2, org):
    user_1 = data.create_rlc_user(rlc=org)
    data.create_rlc_user(email="dummy3@law-orga.de", rlc=org)
    org.generate_keys()
    create_permissions()
    template = RecordTemplate.objects.create(rlc=org, name="Record Template")
    data.create_record(template=template, users=[user_1["user"], rlc_user_2["user"]])
    data.create_record(template=template, users=[user_1["user"], rlc_user_2["user"]])
    yield user_1


def test_get_data_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/rlc_users/data_self/")
    assert response.status_code == 200


def test_update_frontend_settings(user, db):
    c = Client()
    c.login(**user)
    response = c.put("/api/rlc_users/settings_self/", data=json.dumps({"abc": "123"}))
    assert response.status_code == 200


def test_email_confirmation_token_works(user):
    rlc_user = user["rlc_user"]
    generator = EmailConfirmationTokenGenerator()
    token = generator.make_token(rlc_user)
    assert generator.check_token(rlc_user, token)

    ts = generator._num_seconds(datetime.now() - timedelta(days=28))
    token = generator._make_token_with_timestamp(rlc_user, ts)
    assert generator.check_token(rlc_user, token)

    ts = generator._num_seconds(datetime.now() - timedelta(days=32))
    token = generator._make_token_with_timestamp(rlc_user, ts)
    assert not generator.check_token(rlc_user, token)


def test_update_user(user, db):
    c = Client()
    c.login(**user)
    response = c.put(
        "/api/rlc_users/{}/update_information/".format(user["rlc_user"].pk),
        data=json.dumps({"name": "New Name", "note": "New Note"}),
    )
    response_data = response.json()
    assert (
        response.status_code == 200
        and response_data["note"] == "New Note"
        and response_data["name"] == "New Name"
    )


def test_update_another_user_forbidden(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    response = c.put(
        "/api/rlc_users/{}/update_information/".format(rlc_user_2["rlc_user"].pk),
        data=json.dumps({"name": "New Name", "note": "New Note"}),
    )
    assert response.status_code == 400


def test_update_another_user_allowed(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    response = c.put(
        "/api/rlc_users/{}/update_information/".format(rlc_user_2["rlc_user"].pk),
        data=json.dumps({"name": "New Name", "note": "New Note"}),
    )
    response_data = response.json()
    assert (
        response.status_code == 200
        and response_data["note"] == "New Note"
        and response_data["name"] == "New Name"
    )


def test_list_rlc_users(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/rlc_users/")
    response_data = response.json()
    assert response.status_code == 200 and "street" not in response_data[0]


def test_retrieve_rlc_user(user, db):
    c = Client()
    c.login(**user)
    ru = user["rlc_user"]
    response = c.get("/api/rlc_users/{}/".format(ru.id))
    response_data = response.json()
    assert response.status_code == 200 and response_data["street"] is None


def test_retrieve_another_rlc_user(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    ru = rlc_user_2["rlc_user"]
    ru_update = RlcUser.objects.get(id=ru.id)
    ru_update.street = "ABC"
    ru_update.save()
    response = c.get("/api/rlc_users/{}/".format(ru.id))
    response_data = response.json()
    assert response.status_code == 200 and response_data["street"] is None


def test_retrieve_another_rlc_user_with_permission(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    ru = rlc_user_2["rlc_user"]
    ru_update = RlcUser.objects.get(id=ru.id)
    ru_update.street = "ABC"
    ru_update.save()
    response = c.get("/api/rlc_users/{}/".format(ru.id))
    response_data = response.json()
    assert response.status_code == 200 and response_data["street"] == "ABC"


def test_activate_error(user, db):
    c = Client()
    c.login(**user)
    ru = user["rlc_user"]
    response = c.get("/api/rlc_users/{}/activate/".format(ru.id))
    assert response.status_code == 400


def test_activate_error_permission(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    ru = rlc_user_2["rlc_user"]
    response = c.post("/api/rlc_users/{}/activate/".format(ru.id))
    assert response.status_code == 400


def test_activate_success(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    ru = rlc_user_2["rlc_user"]
    response = c.post("/api/rlc_users/{}/activate/".format(ru.id))
    response_data = response.json()
    assert (
        response.status_code == 200
        and RlcUser.objects.get(id=ru.id).is_active is False
        and response_data["email"] == ru.email
        and response_data["is_active"] is not ru.is_active
    )
