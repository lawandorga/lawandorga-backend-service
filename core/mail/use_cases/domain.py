from core.mail.models import MailDomain, MailUser
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def add_domain(__actor: MailUser, domain: str):
    if MailDomain.objects.filter(name=domain).exists():
        raise UseCaseError("This domain is already in use.")

    MailDomain.objects.create(org=__actor.org, name=domain)