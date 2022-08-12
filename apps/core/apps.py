from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class ApiConfig(AppConfig):
    name = "apps.core"

    def ready(self):
        # rlc permissions
        from apps.core.fixtures import create_permissions
        from apps.core.models import Permission

        try:
            Permission.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        create_permissions()

        # files permissions
        from apps.core.fixtures import create_folder_permissions
        from apps.core.models import FolderPermission

        try:
            FolderPermission.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        create_folder_permissions()

        # collab permissions
        from apps.core.fixtures import create_collab_permissions
        from apps.core.models import CollabPermission

        try:
            CollabPermission.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        create_collab_permissions()
