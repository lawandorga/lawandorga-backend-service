from apps.collab.models import CollabPermission
from apps.collab.static import get_all_collab_permission_strings


def create_collab_permissions():
    permissions = get_all_collab_permission_strings()
    for permission in permissions:
        CollabPermission.objects.get_or_create(name=permission)
