from core.mail.models import MailAlias, MailDomain, MailUser


def domain_from_id(actor, v):
    return MailDomain.objects.get(id=v, org__id=actor.org_id)


def alias_from_id(actor, v):
    return MailAlias.objects.get(id=v, user__org__id=actor.org_id)


def mail_user_from_id(actor, v):
    return MailUser.objects.get(id=v, org__id=actor.org_id)
