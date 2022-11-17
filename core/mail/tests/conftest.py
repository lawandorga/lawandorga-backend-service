import pytest

from core.mail.models import MailAccount, MailAddress, MailDomain, MailOrg, MailUser
from core.seedwork import test_helpers


@pytest.fixture
def user(db):
    rlc_user = test_helpers.create_rlc_user(rlc=test_helpers.create_org())
    yield rlc_user["user"]


@pytest.fixture
def two_users_same_org(db):
    rlc_user_1 = test_helpers.create_rlc_user(rlc=test_helpers.create_org())
    org = rlc_user_1["rlc_user"].org
    rlc_user_2 = test_helpers.create_rlc_user(email="dummy2@law-orga.de", rlc=org)
    yield {1: rlc_user_1["user"], 2: rlc_user_2["user"]}


@pytest.fixture
def two_users_different_org(db):
    rlc_user_1 = test_helpers.create_rlc_user(rlc=test_helpers.create_org())
    rlc_user_2 = test_helpers.create_rlc_user(
        email="dummy2@law-orga.de", rlc=test_helpers.create_org()
    )
    yield {1: rlc_user_1["user"], 2: rlc_user_2["user"]}


@pytest.fixture
def mail_org(db):
    mail_org = MailOrg.objects.create()
    yield mail_org


@pytest.fixture
def mail_user(db, mail_org):
    user = test_helpers.create_user(email="dummy3@law-orga.de")
    mail_user = MailUser.objects.create(user=user, org=mail_org, pw_hash="")
    MailAccount.objects.create(user=mail_user)
    yield mail_user


@pytest.fixture
def domain(db, mail_org):
    yield MailDomain.objects.create(name="mail.law-orga.de", org=mail_org)


@pytest.fixture
def alias(db, mail_user, domain):
    yield MailAddress.objects.create(
        localpart="test", domain=domain, account=mail_user.account
    )
