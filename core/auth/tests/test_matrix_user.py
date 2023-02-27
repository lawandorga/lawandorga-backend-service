import pytest

from core.auth.oidc_provider_settings import userinfo
from core.models import MatrixUser, Org, UserProfile
from core.seedwork import test_helpers


@pytest.fixture
def user1(db):
    org = Org.objects.create(name="Test RLC")
    rlc_user = test_helpers.create_rlc_user(rlc=org)
    user = rlc_user["user"]
    m_user = MatrixUser.objects.create(user=user)
    yield m_user


@pytest.fixture
def user2(db):
    org = Org.objects.create(name="Test RLC")
    rlc_user = test_helpers.create_rlc_user(rlc=org, email="tester1@law-orga.de")
    user = rlc_user["user"]
    m_user = MatrixUser.objects.create(user=user, _group="Different Group")
    yield m_user


@pytest.fixture
def user3(db):
    user = UserProfile.objects.create(email="tester2@law-orga.de", name="Tester2")
    user.set_password("pass1234")
    user.save()
    m_user = MatrixUser.objects.create(user=user)
    yield m_user


def test_groups_of_users(db, user1, user2, user3):
    assert user1.group == "Test RLC"
    assert user2.group == "Different Group"
    assert user3.group == ""


def test_userinfo(db, user1):
    claims = userinfo({}, user1.user)
    assert claims["name"] == "Dummy 1"
    assert claims["email"] == "dummy@law-orga.de"
