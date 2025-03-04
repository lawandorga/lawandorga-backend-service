import json
from datetime import datetime, timedelta

import pytest
from django.test import Client

from core.auth.models import OrgUser
from core.auth.token_generator import EmailConfirmationTokenGenerator
from core.auth.use_cases.org_user import activate_rlc_user, update_user_data
from core.data_sheets.models import DataSheetTemplate
from core.models import Org
from core.permissions.static import PERMISSION_ADMIN_MANAGE_USERS
from core.seedwork import test_helpers as data
from core.seedwork.use_case_layer import UseCaseError


@pytest.fixture
def org(db):
    org = Org.objects.create(name="Test RLC")
    yield org


@pytest.fixture
def rlc_user_2(db, org):
    user_2 = data.create_org_user(email="dummy2@law-orga.de", rlc=org)
    yield user_2


@pytest.fixture
def user(db, rlc_user_2, org):
    user_1 = data.create_org_user(rlc=org)
    data.create_org_user(email="dummy3@law-orga.de", rlc=org)
    org.generate_keys()
    template = DataSheetTemplate.objects.create(rlc=org, name="Record Template")
    data.create_data_sheet(
        template=template, users=[user_1["user"], rlc_user_2["user"]]
    )
    data.create_data_sheet(
        template=template, users=[user_1["user"], rlc_user_2["user"]]
    )
    yield user_1


def test_get_data_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/rlc_users/data_self/")
    assert response.status_code == 200


def test_update_frontend_settings(user, db):
    c = Client()
    c.login(**user)
    response = c.post(
        "/api/command/",
        data=json.dumps(
            {"action": "auth/update_frontend_settings", "data": {"abc": "123"}}
        ),
        content_type="application/json",
    )
    assert response.status_code == 200, response.json()


def test_email_confirmation_token_works(user):
    rlc_user = user["rlc_user"]
    generator = EmailConfirmationTokenGenerator()
    token = generator.make_token(rlc_user)
    assert generator.check_token(rlc_user, token)

    ts = generator._num_seconds(datetime.now() - timedelta(days=28))
    token = generator._make_token_with_timestamp(rlc_user, ts)
    assert generator.check_token(rlc_user, token)

    ts = generator._num_seconds(datetime.now() - timedelta(days=400))
    token = generator._make_token_with_timestamp(rlc_user, ts)
    assert not generator.check_token(rlc_user, token)


def test_update_user(user, db):
    update_user_data(
        user["rlc_user"],
        user["rlc_user"].pk,
        **{"name": "New Name", "note": "New Note"},
    )
    user = OrgUser.objects.get(id=user["rlc_user"].id)
    assert user.note == "New Note" and user.name == "New Name"


def test_update_another_user_forbidden(user, rlc_user_2, db):
    with pytest.raises(UseCaseError):
        update_user_data(
            user["rlc_user"],
            rlc_user_2["rlc_user"].pk,
            **{"name": "New Name", "note": "New Note"},
        )


def test_update_another_user_allowed(user, rlc_user_2, db):
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    update_user_data(
        user["rlc_user"],
        rlc_user_2["rlc_user"].pk,
        **{"name": "New Name", "note": "New Note"},
    )
    user = OrgUser.objects.get(id=rlc_user_2["rlc_user"].id)
    assert user.note == "New Note" and user.name == "New Name"


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
    assert response.status_code == 200 and response_data["user"]["street"] is None


def test_retrieve_another_rlc_user(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    ru = rlc_user_2["rlc_user"]
    ru_update = OrgUser.objects.get(id=ru.id)
    ru_update.street = "ABC"
    ru_update.save()
    response = c.get("/api/rlc_users/{}/".format(ru.id))
    response_data = response.json()
    assert response.status_code == 200 and response_data["user"]["street"] is None


def test_retrieve_another_rlc_user_with_permission(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    ru = rlc_user_2["rlc_user"]
    ru_update = OrgUser.objects.get(id=ru.id)
    ru_update.street = "ABC"
    ru_update.save()
    response = c.get("/api/rlc_users/{}/".format(ru.id))
    response_data = response.json()
    assert response.status_code == 200 and response_data["user"]["street"] == "ABC"


def test_activate_error_permission(user, rlc_user_2, db):
    ru = rlc_user_2["rlc_user"]
    with pytest.raises(UseCaseError):
        activate_rlc_user(user["rlc_user"], ru.id)


def test_activate_success(user, rlc_user_2, db):
    c = Client()
    c.login(**user)
    user["rlc_user"].grant(PERMISSION_ADMIN_MANAGE_USERS)
    ru = rlc_user_2["rlc_user"]
    activate_rlc_user(user["rlc_user"], ru.id)
    assert OrgUser.objects.get(id=ru.id).is_active is False
