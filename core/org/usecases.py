from core.org.use_cases.group import (
    add_member_to_group,
    correct_group_keys_of_others,
    create_group,
    delete_group,
    remove_member_from_group,
    update_group,
)
from core.org.use_cases.link import create_link, delete_link
from core.org.use_cases.note import create_note, delete_note, update_note
from core.org.use_cases.org import accept_member_to_org, update_org

USECASES = {
    "org/create_group": create_group,
    "org/update_group": update_group,
    "org/delete_group": delete_group,
    "org/optimize_groups": correct_group_keys_of_others,
    "org/add_member_to_group": add_member_to_group,
    "org/remove_member_from_group": remove_member_from_group,
    "org/create_note": create_note,
    "org/update_note": update_note,
    "org/delete_note": delete_note,
    "org/accept_member_to_org": accept_member_to_org,
    "org/create_link": create_link,
    "org/delete_link": delete_link,
    "org/update_org": update_org,
}
