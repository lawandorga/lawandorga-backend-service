from core.folders.use_cases.folder import invalidate_folder_keys
from messagebus import MessageBus


def ready():
    MessageBus.register_handler("OrgUserLocked", invalidate_folder_keys)
