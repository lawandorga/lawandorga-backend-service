from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class CollabConfig(AppConfig):
    name = "apps.collab"

    def ready(self):
        from apps.collab.fixtures import create_collab_permissions
        from apps.collab.models import CollabPermission

        try:
            CollabPermission.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        create_collab_permissions()
