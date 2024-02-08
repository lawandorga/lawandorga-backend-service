from core.mail.use_cases.domain import add_domain, change_domain
from core.mail.use_cases.group import (
    add_address_to_group,
    add_member_to_group,
    create_group_mail,
    delete_group_address,
    delete_group_mail,
    remove_member_from_group,
    set_group_address_as_default,
)
from core.mail.use_cases.user import (
    create_address,
    create_mail_user,
    delete_address,
    set_address_as_default,
)

USECASES = {
    "mail/add_domain": add_domain,
    "mail/change_domain": change_domain,
    "mail/add_address_to_group": add_address_to_group,
    "mail/create_group": create_group_mail,
    "mail/delete_group": delete_group_mail,
    "mail/add_member_to_group": add_member_to_group,
    "mail/remove_member_from_group": remove_member_from_group,
    "mail/set_default_group_address": set_group_address_as_default,
    "mail/delete_group_address": delete_group_address,
    "mail/create_user": create_mail_user,
    "mail/create_address": create_address,
    "mail/delete_address": delete_address,
    "mail/set_address_as_default": set_address_as_default,
}
