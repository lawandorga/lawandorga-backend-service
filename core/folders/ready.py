from core.folders.use_cases.folder import correct_folder_keys, invalidate_folder_keys
from messagebus import MessageBus


def ready():
    MessageBus.register_handler("OrgUserLocked", invalidate_folder_keys)
    MessageBus.register_handler("OrgUserUnlocked", correct_folder_keys)
