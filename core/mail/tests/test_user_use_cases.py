import pytest
from django.db import IntegrityError

from core.mail.models import MailAccount, MailAddress, MailOrg, MailUser
from core.mail.models.group import MailGroup
from core.mail.use_cases.user import (
    create_address,
    create_mail_user,
    delete_address,
    set_address_as_default,
)
from core.seedwork.use_case_layer import UseCaseError


def test_create_mail_user(db, user):
    create_mail_user(user)


def test_create_multiple_mail_user(db, two_users_same_org):
    create_mail_user(two_users_same_org[1])
    create_mail_user(two_users_same_org[2])
    assert MailOrg.objects.count() == 1


def test_create_mail_user_different_org(db, two_users_different_org):
    create_mail_user(two_users_different_org[1])
    create_mail_user(two_users_different_org[2])
    assert MailOrg.objects.count() == 2


def test_account_constraints(db, user, mail_org):
    mail_user = MailUser.objects.create(user=user, org=mail_org, pw_hash="")
    mail_group = MailGroup.objects.create(org=mail_user.org)
    MailAccount.objects.create(group=mail_group)
    MailAccount.objects.create(user=mail_user)
    with pytest.raises(IntegrityError):
        MailAccount.objects.create(group=mail_group, user=mail_user)


def test_account_constraints_2(db):
    with pytest.raises(IntegrityError):
        MailAccount.objects.create()


def test_create_alias(db, mail_user, domain):
    create_address(
        mail_user, localpart="test", user_uuid=mail_user.uuid, domain_uuid=domain.uuid
    )


def test_create_alias_exists(db, mail_user, domain):
    create_address(
        mail_user, localpart="test", user_uuid=mail_user.uuid, domain_uuid=domain.uuid
    )
    with pytest.raises(UseCaseError):
        create_address(
            mail_user,
            localpart="test",
            user_uuid=mail_user.uuid,
            domain_uuid=domain.uuid,
        )


def test_delete_alias(db, mail_user, alias):
    delete_address(mail_user, alias.uuid)


def test_delete_default_alias(db, mail_user, alias):
    alias.is_default = True
    alias.save()
    with pytest.raises(UseCaseError):
        delete_address(mail_user, alias.uuid)


def test_set_alias_default(db, mail_user, domain, alias):
    alias2 = MailAddress.objects.create(
        localpart="abc", domain=domain, account=mail_user.account, is_default=True
    )
    alias.is_default = True
    alias.save()
    set_address_as_default(mail_user, alias2.uuid)
    assert (
        MailAddress.objects.filter(account__user=mail_user, is_default=True).count()
        == 1
    )


def test_create_alias_invalid_schema(db, mail_user, domain):
    with pytest.raises(ValueError):
        create_address(
            mail_user,
            localpart="invalid#localpart",
            user_uuid=mail_user.uuid,
            domain_uuid=domain.uuid,
        )
