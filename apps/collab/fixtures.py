from apps.collab.static import get_all_collab_permission_strings
from apps.collab.models import CollabPermission


def create_collab_permissions():
    permissions = get_all_collab_permission_strings()
    for permission in permissions:
        CollabPermission.objects.get_or_create(name=permission)
