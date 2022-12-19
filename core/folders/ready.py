from core.folders.use_cases.folder import (
    correct_folder_keys,
    invalidate_folder_keys,
    item_name_changed,
)
from messagebus import MessageBus


def ready():
    MessageBus.register_handler("OrgUserLocked", invalidate_folder_keys)
    MessageBus.register_handler("OrgUserUnlocked", correct_folder_keys)
    MessageBus.register_handler("ItemRenamed", item_name_changed)
