from apps.core.models import Permission, CollabPermission, FolderPermission
from apps.core.static import get_all_permission_strings, get_all_collab_permission_strings, get_all_files_permission_strings


def create_collab_permissions():
    permissions = get_all_collab_permission_strings()
    for permission in permissions:
        CollabPermission.objects.get_or_create(name=permission)


def create_permissions():
    permissions = get_all_permission_strings()
    for permission in permissions:
        Permission.objects.get_or_create(name=permission)


def create_folder_permissions():
    permissions = get_all_files_permission_strings()
    for permission in permissions:
        FolderPermission.objects.get_or_create(name=permission)
