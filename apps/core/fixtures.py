from apps.core.models import Permission, CollabPermission
from apps.core.static import get_all_permission_strings
from apps.core.static import get_all_collab_permission_strings


def create_collab_permissions():
    permissions = get_all_collab_permission_strings()
    for permission in permissions:
        CollabPermission.objects.get_or_create(name=permission)


def create_permissions():
    permissions = get_all_permission_strings()
    for permission in permissions:
        Permission.objects.get_or_create(name=permission)
