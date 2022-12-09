from django.db import transaction

from core.mail.models import MailAccount, MailAddress, MailUser
from core.mail.models.group import MailGroup
from core.mail.use_cases.finders import (
    mail_address_from_id,
    mail_domain_from_uuid,
    mail_group_from_id,
    mail_user_from_id,
)
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def create_group_mail(
    __actor: MailUser, localpart: str, domain=find(mail_domain_from_uuid)
):
    MailAddress.check_localpart(localpart)

    if MailAddress.objects.filter(localpart=localpart, domain=domain):
        raise UseCaseError("This mail is already in use.")

    group = MailGroup(org=__actor.org)
    account = MailAccount(group=group)
    address = MailAddress(
        localpart=localpart, domain=domain, is_default=True, account=account
    )
    with transaction.atomic():
        group.save()
        account.save()
        address.save()
        group.members.add(__actor)


@use_case
def delete_group_mail(__actor: MailUser, group=find(mail_group_from_id)):
    group.delete()


@use_case
def add_member_to_group(
    __actor: MailUser, group=find(mail_group_from_id), member=find(mail_user_from_id)
):
    group.members.add(member)


@use_case
def remove_member_from_group(
    __actor: MailUser, group=find(mail_group_from_id), member=find(mail_user_from_id)
):
    group.members.remove(member)


@use_case
def add_address_to_group(
    __actor: MailUser,
    localpart: str,
    group=find(mail_group_from_id),
    domain=find(mail_domain_from_uuid),
):
    MailAddress.check_localpart(localpart)

    if MailAddress.objects.filter(localpart=localpart, domain=domain).exists():
        raise UseCaseError(
            "An alias with the same localpart and domain exists already."
        )

    is_default = MailAddress.objects.filter(account=group.account).count() == 0
    MailAddress.objects.create(
        account=group.account, localpart=localpart, domain=domain, is_default=is_default
    )


@use_case
def set_group_address_as_default(__actor: MailUser, address=find(mail_address_from_id)):
    with transaction.atomic():
        MailAddress.objects.filter(account=address.account).update(is_default=False)
        address.is_default = True
        address.save()


@use_case
def delete_group_address(__actor: MailUser, address=find(mail_address_from_id)):
    if address.is_default:
        raise UseCaseError("You can not delete the default address.")

    address.delete()
