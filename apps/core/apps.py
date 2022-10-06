from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class CoreConfig(AppConfig):
    name = "apps.core"

    def ready(self):
        # import this file to add use_case mappings
        from apps.core import use_cases  # type: ignore

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

        # record templates
        from apps.core.models import Org
        from apps.core.records.fixtures import create_default_record_template

        try:
            for rlc in Org.objects.all():
                if rlc.recordtemplates.count() == 0:
                    create_default_record_template(rlc)
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
