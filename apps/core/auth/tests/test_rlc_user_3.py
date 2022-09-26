from datetime import datetime, timedelta

import pytest
from django.test import Client

from apps.core.models import Org
from apps.recordmanagement.models import RecordTemplate
from apps.static import test_helpers as data

from ...fixtures import create_permissions
from ..token_generator import EmailConfirmationTokenGenerator


@pytest.fixture
def user(db):
    rlc = Org.objects.create(name="Test RLC")
    user_1 = data.create_rlc_user(rlc=rlc)
    user_2 = data.create_rlc_user(email="dummy2@law-orga.de", rlc=rlc)
    data.create_rlc_user(email="dummy3@law-orga.de", rlc=rlc)
    rlc.generate_keys()
    create_permissions()
    template = RecordTemplate.objects.create(rlc=rlc, name="Record Template")
    data.create_record(template=template, users=[user_1["user"], user_2["user"]])
    data.create_record(template=template, users=[user_1["user"], user_2["user"]])
    yield user_1


def test_get_data_works(user, db):
    c = Client()
    c.login(**user)
    response = c.get("/api/rlc_users/data_self/")
    assert response.status_code == 200


def test_update_frontend_settings(user, db):
    c = Client()
    c.login(**user)
    response = c.put("/api/rlc_users/settings_self/", json={"abc": "123"})
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
