import pytest

from core.mail.models import MailAlias, MailOrg
from core.mail.use_cases.user import (
    create_alias,
    create_mail_user,
    delete_alias,
    set_alias_as_default,
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


def test_create_alias(db, mail_user, domain):
    create_alias(mail_user, localpart="test", user=mail_user.id, domain=domain.id)


def test_create_alias_exists(db, mail_user, domain):
    create_alias(mail_user, localpart="test", user=mail_user.id, domain=domain.id)
    with pytest.raises(UseCaseError):
        create_alias(mail_user, localpart="test", user=mail_user.id, domain=domain.id)


def test_delete_alias(db, mail_user, alias):
    delete_alias(mail_user, alias.id)


def test_delete_default_alias(db, mail_user, alias):
    alias.is_default = True
    alias.save()
    with pytest.raises(UseCaseError):
        delete_alias(mail_user, alias.id)


def test_set_alias_default(db, mail_user, domain, alias):
    alias2 = MailAlias.objects.create(
        localpart="abc", domain=domain, user=mail_user, is_default=True
    )
    alias.is_default = True
    alias.save()
    set_alias_as_default(mail_user, alias2.id)
    assert MailAlias.objects.filter(user=mail_user, is_default=True).count() == 1
