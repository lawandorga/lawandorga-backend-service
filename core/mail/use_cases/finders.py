from django.db.models import Q

from core.mail.models import MailAddress, MailDomain, MailUser


def domain_from_id(actor, v) -> MailDomain:
    return MailDomain.objects.filter(id=v).get(Q(org__id=actor.org_id))


def address_from_id(actor, v) -> MailAddress:
    return MailAddress.objects.get(id=v, account__user__org__id=actor.org_id)


def mail_user_from_id(actor, v) -> MailUser:
    return MailUser.objects.get(id=v, org__id=actor.org_id)
