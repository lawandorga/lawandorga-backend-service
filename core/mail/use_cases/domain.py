from django.db import transaction

from core.mail.models import MailDomain, MailUser
from core.seedwork.use_case_layer import use_case, UseCaseError


@use_case
def add_domain(__actor: MailUser, domain: str):
    if MailDomain.objects.filter(name=domain).exists():
        raise UseCaseError('This domain is already in use.')

    with transaction.atomic():
        d = MailDomain.objects.create(org=__actor.org, name=domain, relative_path="")
        d.relative_path = str(d.id)
        d.save()
