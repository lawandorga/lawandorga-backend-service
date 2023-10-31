from core.mail.use_cases.group import add_member_to_group, remove_member_from_group
from core.rlc.use_cases.group import create_group, delete_group, update_group

COMMANDS = {
    "org/create_group": create_group,
    "org/update_group": update_group,
    "org/delete_group": delete_group,
    "org/add_member_to_group": add_member_to_group,
    "org/remove_member_from_group": remove_member_from_group,
}
