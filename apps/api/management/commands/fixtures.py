from apps.collab.static.collab_permissions import get_all_collab_permission_strings
from apps.api.static import get_all_permissions_strings
from apps.collab.models import CollabPermission
from apps.api.models import Permission


class Fixtures:
    @staticmethod
    def create_real_permissions_no_duplicates():
        permissions = get_all_permissions_strings()
        for permission in permissions:
            Permission.objects.get_or_create(name=permission)

    @staticmethod
    def create_real_collab_permissions():
        permissions = get_all_collab_permission_strings()
        for permission in permissions:
            CollabPermission.objects.get_or_create(name=permission)
