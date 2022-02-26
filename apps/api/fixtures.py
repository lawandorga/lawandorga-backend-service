from apps.api.static import get_all_permission_strings
from apps.api.models import Permission


def create_permissions():
    permissions = get_all_permission_strings()
    for permission in permissions:
        Permission.objects.get_or_create(name=permission)
