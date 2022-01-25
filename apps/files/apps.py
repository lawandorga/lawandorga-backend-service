from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class FilesConfig(AppConfig):
    name = "apps.files"

    def ready(self):
        from apps.files.fixtures import create_folder_permissions
        from apps.files.models import FolderPermission
        try:
            FolderPermission.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        create_folder_permissions()
