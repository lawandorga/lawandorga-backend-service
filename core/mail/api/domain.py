from typing import Union

import dns.resolver

from core.mail.api import schemas
from core.mail.models import MailUser
from core.mail.use_cases.domain import add_domain, change_domain, check_domain_settings
from core.mail.use_cases.finders import mail_domain_from_uuid
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.post(input_schema=schemas.InputAddDomain)
def command__add_domain(mail_user: MailUser, data: schemas.InputAddDomain):
    add_domain(mail_user, data.name)


@router.post(url="<uuid:domain>/", input_schema=schemas.InputChangeDomain)
def command__change_domain(mail_user: MailUser, data: schemas.InputChangeDomain):
    change_domain(mail_user, data.name, data.uuid)


@router.post(
    url="<uuid:domain>/check_domain/",
    input_schema=schemas.InputCheckDomain,
    output_schema=schemas.OutputDomainCheck,
)
def command__check_domain_settings(mail_user: MailUser, data: schemas.InputCheckDomain):
    records: list[str] = []

    domain = mail_domain_from_uuid(mail_user, data.domain)

    try:
        for setting in domain.get_settings():
            for item in dns.resolver.resolve(setting["host"], setting["type"]):
                text = item.to_text().replace('"', "")
                records.append(text)
    except dns.exception.DNSException as e:
        raise ApiError(str(e), status=422)

    wrong_setting = check_domain_settings(mail_user, records, data.domain)

    domain = mail_domain_from_uuid(mail_user, data.domain)

    ret_data: dict[str, Union[list[str], bool]] = {
        "mx_records": records,
        "wrong_setting": wrong_setting,
        "valid": domain.is_active,
    }

    return ret_data
