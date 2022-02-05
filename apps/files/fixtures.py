from apps.files.static import get_all_files_permission_strings
from apps.files.models import FolderPermission


def create_folder_permissions():
    permissions = get_all_files_permission_strings()
    for permission in permissions:
        FolderPermission.objects.get_or_create(name=permission)
