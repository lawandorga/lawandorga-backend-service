from django.db import transaction

from core.auth.models import UserProfile
from core.mail.models import MailAccount, MailAddress, MailOrg, MailUser
from core.mail.use_cases.finders import (
    address_from_id,
    domain_from_id,
    mail_user_from_id,
)
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def create_mail_user(__actor: UserProfile):
    if not hasattr(__actor, "rlc_user"):
        raise UseCaseError(
            "At the moment mail users can only be created for users with an org user role."
        )

    org = __actor.rlc_user.org
    users = [u.user for u in list(org.users.select_related("user").all())]

    mail_org = None
    for u in users:
        if hasattr(u, "mail_user"):
            mail_org = u.mail_user.org
            break

    with transaction.atomic():
        if mail_org is None:
            mail_org = MailOrg.objects.create()

        mail_user = MailUser.objects.create(user=__actor, org=mail_org, pw_hash="")
        MailAccount.objects.create(user=mail_user)


@use_case
def create_address(
    __actor: MailUser,
    localpart: str,
    user=find(mail_user_from_id),
    domain=find(domain_from_id),
):
    if MailAddress.objects.filter(localpart=localpart, domain=domain).exists():
        raise UseCaseError(
            "An alias with the same localpart and domain exists already."
        )

    is_default = MailAddress.objects.filter(account=user.account).count() == 0
    MailAddress.objects.create(account=user.account, localpart=localpart, domain=domain, is_default=is_default)


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
