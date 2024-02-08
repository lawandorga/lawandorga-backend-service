from core.mail.use_cases.domain import add_domain, change_domain, check_domain_settings
from core.mail.use_cases.group import add_address_to_group, add_member_to_group, create_group_mail, delete_group_address, delete_group_mail, remove_member_from_group, set_group_address_as_default


USECASES = {
    "mail/add_domain": add_domain,
    "mail/change_domain": change_domain,
    "mail/add_address_to_group": add_address_to_group,
    "mail/create_group": create_group_mail,
    "mail/delete_group": delete_group_mail,
    "mail/add_member_to_group": add_member_to_group,
    "mail/remove_member_from_group": remove_member_from_group,
    "mail/add_address_to_group": add_address_to_group,
    "mail/set_default_group_address": set_group_address_as_default,
    "mail/delete_group_address": delete_group_address,
}