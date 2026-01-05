import pytest
from django.conf import settings
from django.test import Client

from core.auth.use_cases.org_user import delete_user, unlock_user
from core.auth.use_cases.user import change_password_of_user
from core.folders.domain.value_objects.asymmetric_key import EncryptedAsymmetricKey
from core.models import OrgUser, UserProfile
from core.permissions.static import PERMISSION_ADMIN_MANAGE_USERS
from core.seedwork import test_helpers
from core.seedwork.use_case_layer import UseCaseError


@pytest.fixture
def org_user(db):
    user = test_helpers.create_org_user()
    yield user


def test_email_confirmation_token_works(db, org_user):
    token = org_user["org_user"].get_email_confirmation_token()
    c = Client()
    c.login(**org_user)
    url = "/api/auth/org_users/{}/confirm_email/{}/".format(
        org_user["org_user"].id, token
    )
    response = c.post(url)
    assert 200 == response.status_code


def test_everybody_can_hit_email_confirm(db):
    client = Client()
    response = client.post("/api/auth/org_users/1/confirm_email/token-123/")
    assert response.status_code != 403 and response.status_code != 401


def test_user_can_not_delete_someone_else(db, org_user):
    client = Client()
    client.login(**org_user)
    user = org_user["org_user"]
    another_user = test_helpers.create_org_user(
        email="test122@law-orga.de", org=user.org
    )["org_user"]
    with pytest.raises(UseCaseError):
        delete_user(user, another_user.pk)


def test_unlock_works(db, org_user):
    client = Client()
    client.login(**org_user)
    user = org_user["org_user"]
    another_user = test_helpers.create_org_user(
        email="test5692@law-orga.de", org=user.org
    )["org_user"]
    another_user.locked = True
    another_user.save()
    unlock_user(user, another_user.pk)
    another_user.refresh_from_db()
    assert not another_user.locked


def test_change_password_works(db):
    user = test_helpers.create_raw_org_user(save=True)
    private_key = user.get_private_key()
    data = {
        "current_password": settings.DUMMY_USER_PASSWORD,
        "new_password": "pass1234!",
        "new_password_confirm": "pass1234!",
    }
    change_password_of_user(user.user, **data)
    org_user = OrgUser.objects.get(pk=user.pk)
    user_key = org_user.keyring.get_user_key_from_password("pass1234!")
    assert private_key == user_key.key.get_private_key().decode("utf-8")


def test_delete_works(db, org_user):
    client = Client()
    client.login(**org_user)
    user = org_user["org_user"]
    user.grant(PERMISSION_ADMIN_MANAGE_USERS)
    another_user = test_helpers.create_org_user(
        email="test2@law-orga.de", org=user.org
    )["org_user"]
    org_users = OrgUser.objects.count()
    user_profiles = UserProfile.objects.count()
    delete_user(user, another_user.pk)
    assert OrgUser.objects.count() == org_users - 1
    assert UserProfile.objects.count() == user_profiles - 1


def test_keys_are_generated(db):
    user = test_helpers.create_raw_org_user()
    user.generate_keys(settings.DUMMY_USER_PASSWORD)
    user.org.save()
    user.user.save()
    user.save()
    user = OrgUser.objects.get(pk=user.pk)
    assert isinstance(user.get_encryption_key(), EncryptedAsymmetricKey)
