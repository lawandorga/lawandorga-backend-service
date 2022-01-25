from apps.files.static.folder_permissions import get_all_folder_permissions_strings
from apps.files.models import FolderPermission


def create_folder_permissions():
    permissions = get_all_folder_permissions_strings()
    for permission in permissions:
        FolderPermission.objects.get_or_create(name=permission)
