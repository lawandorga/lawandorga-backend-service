from typing import Callable

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.item import FolderItem
from core.folders.handlers.folder import (
    handler__item_added_to_folder,
    handler__item_deleted,
    handler__item_renamed,
    handler__org_user_locked,
    handler__org_user_unlocked,
)
from core.folders.usecases.folder import (
    correct_folder_keys_of_others,
    create_folder,
    delete_folder,
    grant_access,
    grant_access_to_group,
    move_folder,
    rename_folder,
    revoke_access,
    revoke_access_from_group,
    toggle_inheritance,
)
from messagebus.domain.event import Event

USECASES = {
    "folders/create_folder": create_folder,
    "folders/rename_folder": rename_folder,
    "folders/delete_folder": delete_folder,
    "folders/move_folder": move_folder,
    "folders/toggle_inheritance_folder": toggle_inheritance,
    "folders/grant_access_to_user": grant_access,
    "folders/revoke_access_from_user": revoke_access,
    "folders/grant_access_to_group": grant_access_to_group,
    "folders/revoke_access_from_group": revoke_access_from_group,
    "folders/optimize": correct_folder_keys_of_others,
}

HANDLERS: dict[type[Event], list[Callable]] = {
    FolderItem.ItemRenamed: [handler__item_renamed],
    FolderItem.ItemDeleted: [handler__item_deleted],
    FolderItem.ItemAddedToFolder: [handler__item_added_to_folder],
    OrgUser.OrgUserLocked: [handler__org_user_locked],
    OrgUser.OrgUserUnlocked: [handler__org_user_unlocked],
}
