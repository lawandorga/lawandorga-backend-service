from core.mail.models import MailAddress, MailDomain, MailUser
from core.mail.models.group import MailGroup


def domain_from_id(actor, v) -> MailDomain:
    return MailDomain.objects.filter(uuid=v).get(org__id=actor.org_id)


def address_from_id(actor, v) -> MailAddress:
    return MailAddress.objects.get(uuid=v, account__user__org__id=actor.org_id)


def mail_user_from_id(actor, v) -> MailUser:
    return MailUser.objects.get(uuid=v, org__id=actor.org_id)


def mail_group_from_id(actor, v) -> MailGroup:
    return MailGroup.objects.get(uuid=v, org_id=actor.org_id)
