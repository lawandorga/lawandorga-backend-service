import pytest
from django.db import transaction

from core.mail.models import MailAccount, MailAddress, MailDomain, MailOrg, MailUser
from core.mail.models.group import MailGroup
from core.seedwork import test_helpers


@pytest.fixture
def user(db):
    org_user = test_helpers.create_org_user()
    yield org_user["user"]


@pytest.fixture
def two_users_same_org(db):
    org_user_1 = test_helpers.create_org_user()
    org = org_user_1["org_user"].org
    org_user_2 = test_helpers.create_org_user(email="dummy2@law-orga.de", org=org)
    yield {1: org_user_1["user"], 2: org_user_2["user"]}


@pytest.fixture
def two_users_different_org(db):
    org_user_1 = test_helpers.create_org_user()
    org_user_2 = test_helpers.create_org_user(email="dummy2@law-orga.de")
    yield {1: org_user_1["user"], 2: org_user_2["user"]}


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
def another_mail_user(db, mail_org):
    user = test_helpers.create_user(email="dummy4@law-orga.de")
    mail_user = MailUser.objects.create(user=user, org=mail_org, pw_hash="")
    MailAccount.objects.create(user=mail_user)
    yield mail_user


@pytest.fixture
def mail_group(db, mail_user, domain):
    group = MailGroup(org=mail_user.org)
    account = MailAccount(group=group)
    address = MailAddress(
        localpart="conftest", domain=domain, is_default=True, account=account
    )
    with transaction.atomic():
        group.save()
        account.save()
        address.save()
        group.members.add(mail_user)
    yield group


@pytest.fixture
def domain(db, mail_org):
    yield MailDomain.objects.create(name="mail-abc-xyz.law-orga.de", org=mail_org)


@pytest.fixture
def alias(db, mail_user, domain):
    yield MailAddress.objects.create(
        localpart="test", domain=domain, account=mail_user.account
    )
