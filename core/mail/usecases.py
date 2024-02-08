from core.mail.use_cases.domain import add_domain, change_domain, check_domain_settings


USECASES = {
    "mail/add_domain": add_domain,
    "mail/change_domain": change_domain,
}