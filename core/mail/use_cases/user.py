from django.db import transaction

from core.auth.models import UserProfile
from core.mail.models import MailAlias, MailOrg, MailUser
from core.mail.use_cases.finders import alias_from_id, domain_from_id
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

        mail_user = MailUser.objects.create(
            user=__actor, org=mail_org, pw_hash="", relative_path=""
        )
        mail_user.relative_path = str(mail_user.pk)
        mail_user.save()


@use_case
def create_alias(__actor: MailUser, localpart: str, domain=find(domain_from_id)):
    if MailAlias.objects.filter(localpart=localpart, domain=domain).exists():
        raise UseCaseError(
            "An alias with the same localpart and domain exists already."
        )

    MailAlias.objects.create(user=__actor, localpart=localpart, domain=domain)


@use_case
def set_alias_as_default(__actor: MailUser, alias=find(alias_from_id)):
    with transaction.atomic():
        MailAlias.objects.filter(user=__actor).update(is_default=False)
        alias.is_default = True
        alias.save()


@use_case
def delete_alias(__actor: MailUser, alias=find(alias_from_id)):
    if alias.is_default:
        raise UseCaseError("You can not delete the default alias.")

    alias.delete()
