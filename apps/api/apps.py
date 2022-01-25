from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class ApiConfig(AppConfig):
    name = "apps.api"

    def ready(self):
        from apps.api.fixtures import create_permissions
        from apps.api.models import Permission
        try:
            Permission.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        create_permissions()
