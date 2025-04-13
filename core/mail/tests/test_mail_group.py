import pytest

from core.mail.models import MailAddress
from core.mail.models.group import MailGroup
from core.mail.use_cases.group import (
    add_address_to_group,
    add_member_to_group,
    create_group_mail,
    delete_group_address,
    delete_group_mail,
    remove_member_from_group,
    set_group_address_as_default,
)
from core.seedwork.domain_layer import DomainError


def test_create_group(db, mail_user, domain):
    create_group_mail(mail_user, localpart="test", domain_uuid=domain.uuid)
    address = MailAddress.objects.get(localpart="test", domain=domain)
    assert mail_user in address.account.group.members.all()


def test_delete_group(db, mail_user, mail_group):
    delete_group_mail(mail_user, group_uuid=mail_group.uuid)
    assert not MailGroup.objects.filter(id=mail_group.id)


def test_add_member_to_group(db, mail_user, mail_group, another_mail_user):
    add_member_to_group(mail_user, mail_group.uuid, another_mail_user.uuid)
    assert another_mail_user in mail_group.members.all()


def test_remove_member_from_group(db, mail_user, mail_group, another_mail_user):
    add_member_to_group(mail_user, mail_group.uuid, another_mail_user.uuid)
    remove_member_from_group(mail_user, mail_group.uuid, another_mail_user.uuid)
    assert another_mail_user not in mail_group.members.all()


def test_add_address_to_group(db, mail_user, mail_group, domain):
    add_address_to_group(mail_user, "custom", mail_group.uuid, domain.uuid)
    assert MailAddress.objects.filter(localpart="custom", domain=domain).exists()


def test_set_address_as_default(db, mail_user, mail_group, domain):
    add_address_to_group(mail_user, "custom", mail_group.uuid, domain.uuid)
    address = MailAddress.objects.filter(localpart="custom", domain=domain).get()
    set_group_address_as_default(mail_user, address.uuid)
    assert (
        MailAddress.objects.filter(localpart="custom", domain=domain).get().is_default
    )


def test_delete_group_address(db, mail_user, mail_group, domain):
    add_address_to_group(mail_user, "custom", mail_group.uuid, domain.uuid)
    address = MailAddress.objects.filter(localpart="custom", domain=domain).get()
    delete_group_address(mail_user, address.uuid)
    assert not MailAddress.objects.filter(localpart="custom", domain=domain).exists()


def test_add_address_block_with_invalid_format(db, mail_user, mail_group, domain):
    with pytest.raises(DomainError):
        add_address_to_group(
            mail_user, "invalid%localpart", mail_group.uuid, domain.uuid
        )


def test_create_group_with_invalid_localpart(db, mail_user, domain):
    with pytest.raises(DomainError):
        create_group_mail(mail_user, localpart="AFLJKFD", domain_uuid=domain.uuid)
