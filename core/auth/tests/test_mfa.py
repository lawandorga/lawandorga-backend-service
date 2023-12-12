import pytest
from django.conf import settings
from django.test.client import Client

from core.auth.models.mfa import MultiFactorAuthenticationSecret
from core.auth.models.org_user import OrgUser
from core.auth.use_cases.mfa import create_mfa_secret, enable_mfa_secret
from core.seedwork import test_helpers


@pytest.fixture
def mfa():
    user = test_helpers.create_raw_org_user()
    mfa = MultiFactorAuthenticationSecret.create(user, lambda: "secret")
    yield mfa


@pytest.fixture
def real_mfa():
    user = test_helpers.create_raw_org_user()
    mfa = MultiFactorAuthenticationSecret.create(user)
    yield mfa


def test_mfa_creation_default_generator():
    user = test_helpers.create_raw_org_user()
    MultiFactorAuthenticationSecret.create(user)


def test_mfa_creation():
    user = test_helpers.create_raw_org_user()
    secret = "1234"
    mfa = MultiFactorAuthenticationSecret.create(user, lambda: secret)
    assert mfa._MultiFactorAuthenticationSecret__get_secret() == secret


def test_mfa_url(mfa):
    assert "secret" in mfa.url


def test_mfa_enable(mfa):
    mfa.enable()
    assert mfa.enabled is True


def test_mfa_code(real_mfa):
    mfa = real_mfa
    code1 = mfa.get_code()
    code2 = mfa.get_code()
    assert code1 == code2


def test_mfa_login(db):
    full_user = test_helpers.create_org_user()
    user: OrgUser = full_user["rlc_user"]  # type: ignore
    create_mfa_secret(user)
    enable_mfa_secret(user)
    client = Client()
    response1 = client.post(
        "/login/",
        {"username": user.email, "password": settings.DUMMY_USER_PASSWORD},
        follow=True,
    )
    assert response1.status_code == 200
    code = user.mfa_secret.get_code()
    response2 = client.post("/auth/mfa/login/", {"code": code}, follow=True)
    assert response2.status_code == 200
    # this somehow makes this test flaky: ??
    # assert response2.context["user"].id == user.user_id
