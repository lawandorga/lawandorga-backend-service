import json

import pytest
from django.conf import settings
from django.test import Client

from core.folders.domain.value_objects.asymmetric_key import EncryptedAsymmetricKey
from core.models import RlcUser, UserProfile
from core.seedwork import test_helpers
from core.static import PERMISSION_ADMIN_MANAGE_USERS


@pytest.fixture
def rlc_user(db):
    user = test_helpers.create_rlc_user()
    yield user


def test_email_confirmation_token_works(db, rlc_user):
    token = rlc_user["rlc_user"].get_email_confirmation_token()
    c = Client()
    c.login(**rlc_user)
    url = "/api/rlc_users/{}/confirm_email/{}/".format(rlc_user["rlc_user"].id, token)
    response = c.post(url)
    assert 200 == response.status_code


def test_not_everybody_can_hit_destroy(db):
    client = Client()
    response = client.delete("/api/rlc_users/1/")
    assert 401 == response.status_code


def test_everybody_can_hit_email_confirm(db):
    client = Client()
    response = client.post("/api/rlc_users/1/confirm_email/token-123/")
    assert response.status_code != 403 and response.status_code != 401


def test_not_everybody_can_hit_unlock(db):
    client = Client()
    response = client.post("/api/rlc_users/1/unlock_user/")
    assert 401 == response.status_code


def test_user_can_not_delete_someone_else(db, rlc_user):
    client = Client()
    client.login(**rlc_user)
    user = rlc_user["rlc_user"]
    another_user = test_helpers.create_rlc_user(
        email="test2@law-orga.de", rlc=user.org
    )["rlc_user"]
    response = client.delete("/api/rlc_users/{}/".format(another_user.pk))
    assert response.status_code == 400


def test_unlock_works(db, rlc_user):
    client = Client()
    client.login(**rlc_user)
    user = rlc_user["rlc_user"]
    another_user = test_helpers.create_rlc_user(
        email="test2@law-orga.de", rlc=user.org
    )["rlc_user"]
    another_user.locked = True
    another_user.save()
    response = client.post("/api/rlc_users/{}/unlock_user/".format(another_user.pk))
    assert response.status_code == 200


def test_change_password_works(db, rlc_user):
    client = Client()
    client.login(**rlc_user)
    user = rlc_user["rlc_user"]
    private_key = user.get_private_key()
    data = {
        "current_password": settings.DUMMY_USER_PASSWORD,
        "new_password": "pass1234!",
        "new_password_confirm": "pass1234!",
    }
    response = client.post(
        "/api/users/change_password/",
        data=json.dumps(data),
        content_type="application/json",
    )
    assert response.status_code == 200
    rlc_user = RlcUser.objects.get(pk=user.pk)
    user_key = rlc_user.get_decrypted_key_from_password("pass1234!")
    assert private_key == user_key.key.get_private_key().decode("utf-8")


def test_delete_works(db, rlc_user):
    client = Client()
    client.login(**rlc_user)
    user = rlc_user["rlc_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_USERS)
    another_user = test_helpers.create_rlc_user(
        email="test2@law-orga.de", rlc=user.org
    )["rlc_user"]
    rlc_users = RlcUser.objects.count()
    user_profiles = UserProfile.objects.count()
    response = client.delete("/api/rlc_users/{}/".format(another_user.pk))
    assert response.status_code == 200
    assert RlcUser.objects.count() == rlc_users - 1
    assert UserProfile.objects.count() == user_profiles - 1


def test_keys_are_generated(rlc_user):
    user = rlc_user["rlc_user"]
    user.generate_keys(settings.DUMMY_USER_PASSWORD)
    user.save()
    user = RlcUser.objects.get(pk=user.pk)
    assert isinstance(user.get_encryption_key(), EncryptedAsymmetricKey)
