import pytest

from core.auth.models.mfa import MultiFactorAuthenticationSecret
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
    assert mfa.__get_secret() == secret


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
