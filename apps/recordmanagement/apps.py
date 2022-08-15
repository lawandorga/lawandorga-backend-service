from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class RecordmanagementConfig(AppConfig):
    name = "apps.recordmanagement"

    def ready(self):
        from apps.core.models import Org
        from apps.recordmanagement.fixtures import create_default_record_template

        # from apps.recordmanagement.models import RecordTemplate, RecordStandardField, RecordEncryptedStandardField, \
        #     OriginCountry, RecordUsersField, RecordStateField, RecordSelectField, RecordMultipleField
        try:
            for rlc in Org.objects.all():
                if rlc.recordtemplates.count() == 0:
                    create_default_record_template(rlc)
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
