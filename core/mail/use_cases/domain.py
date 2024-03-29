from uuid import UUID

from core.mail.models import MailDomain, MailUser
from core.mail.models.domain import DnsResults
from core.mail.use_cases.finders import mail_domain_from_uuid
from core.permissions.static import PERMISSION_MAIL_MANAGE_ACCOUNTS
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case(permissions=[PERMISSION_MAIL_MANAGE_ACCOUNTS])
def add_domain(__actor: MailUser, domain: str):
    MailDomain.check_domain(domain)

    if MailDomain.objects.filter(name=domain).exists():
        raise UseCaseError("This domain is already in use.")

    d = MailDomain(org=__actor.org)
    d.set_name(domain)
    d.save()


@use_case(permissions=[PERMISSION_MAIL_MANAGE_ACCOUNTS])
def change_domain(__actor: MailUser, name: str, domain_uuid: UUID):
    domain = mail_domain_from_uuid(__actor, domain_uuid)
    MailDomain.check_domain(name)

    domain.set_name(name)
    domain.save()


@use_case
def check_domain_settings(
    __actor: MailUser, dns_results: DnsResults, domain_uuid: UUID
) -> str | None:
    domain = mail_domain_from_uuid(__actor, domain_uuid)
    _, wrong_setting = domain.check_settings(dns_results)
    domain.save()
    return wrong_setting
