from typing import Literal, Union

import dns.resolver

from core.mail.api import schemas
from core.mail.models import MailUser
from core.mail.models.domain import DnsResults, DnsSetting
from core.mail.use_cases.domain import add_domain, change_domain, check_domain_settings
from core.mail.use_cases.finders import mail_domain_from_uuid
from core.seedwork.api_layer import Router

router = Router()


@router.post()
def command__add_domain(mail_user: MailUser, data: schemas.InputAddDomain):
    add_domain(mail_user, data.name)


@router.post(url="<uuid:domain>/")
def command__change_domain(mail_user: MailUser, data: schemas.InputChangeDomain):
    change_domain(mail_user, data.name, data.uuid)


@router.post(
    url="<uuid:domain>/check_domain/",
    output_schema=schemas.OutputDomainCheck,
)
def command__check_domain_settings(mail_user: MailUser, data: schemas.InputCheckDomain):
    results: DnsResults = {"MX": "", "DKIM": "", "SPF": "", "DMARC": ""}

    domain = mail_domain_from_uuid(mail_user, data.domain)

    for key, setting in domain.get_settings().items():
        k: Literal["MX", "DKIM", "DMARC", "SPF"] = key  # type: ignore
        s: DnsSetting = setting  # type: ignore

        try:
            dns_result = dns.resolver.resolve(s["host"], s["type"])
        except dns.exception.DNSException as e:
            dns_result = None
            results[k] = str(e)

        if dns_result is not None:
            local_results = []
            for item in dns_result:
                text = item.to_text().replace('"', "")
                local_results.append(text)

            results[k] = local_results

    wrong_setting = check_domain_settings(mail_user, results, data.domain)

    domain = mail_domain_from_uuid(mail_user, data.domain)

    ret_data: dict[str, Union[list[str], bool]] = {
        "wrong_setting": wrong_setting,
        "valid": domain.is_active,
    }

    return ret_data
