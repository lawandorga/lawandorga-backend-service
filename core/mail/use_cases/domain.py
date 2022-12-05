from core.mail.models import MailDomain, MailUser
from core.mail.use_cases.finders import mail_domain_from_id
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def add_domain(__actor: MailUser, domain: str):
    MailDomain.check_domain(domain)

    if MailDomain.objects.filter(name=domain).exists():
        raise UseCaseError("This domain is already in use.")

    MailDomain.objects.create(org=__actor.org, name=domain)


@use_case
def change_domain(__actor: MailUser, name: str, domain=find(mail_domain_from_id)):
    MailDomain.check_domain(name)

    domain.name = name
    domain.save()
