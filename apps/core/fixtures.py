from apps.core.models import Permission
from apps.core.static import get_all_permission_strings


def create_permissions():
    permissions = get_all_permission_strings()
    for permission in permissions:
        Permission.objects.get_or_create(name=permission)
