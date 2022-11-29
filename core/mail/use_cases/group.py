from django.db import transaction

from core.mail.models import MailAddress, MailUser
from core.mail.use_cases.finders import (
    address_from_id,
    domain_from_id,
    mail_group_from_id,
    mail_user_from_id,
)
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def create_group(__actor: MailUser, name: str):
    pass


@use_case
def delete_group(__actor: MailUser, name: str):
    pass


@use_case
def add_member_to_group(__actor: MailUser, member=find(mail_user_from_id)):
    pass


@use_case
def remove_member_from_group(__actor: MailUser, member=find(mail_user_from_id)):
    pass


@use_case
def create_address(
    __actor: MailUser,
    localpart: str,
    group=find(mail_group_from_id),
    domain=find(domain_from_id),
):
    if MailAddress.objects.filter(localpart=localpart, domain=domain).exists():
        raise UseCaseError(
            "An alias with the same localpart and domain exists already."
        )

    is_default = MailAddress.objects.filter(account=group.account).count() == 0
    MailAddress.objects.create(
        account=group.account, localpart=localpart, domain=domain, is_default=is_default
    )


@use_case
def set_address_as_default(__actor: MailUser, address=find(address_from_id)):
    with transaction.atomic():
        MailAddress.objects.filter(account=address.account).update(is_default=False)
        address.is_default = True
        address.save()


@use_case
def delete_address(__actor: MailUser, address=find(address_from_id)):
    if address.is_default:
        raise UseCaseError("You can not delete the default address.")

    address.delete()
