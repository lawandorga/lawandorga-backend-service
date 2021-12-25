from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class RecordmanagementConfig(AppConfig):
    name = "apps.recordmanagement"

    def ready(self):
        from apps.recordmanagement.fixtures import create_default_record_template
        from apps.api.models import Rlc
        from apps.recordmanagement.models import RecordTemplate, RecordStandardField, RecordEncryptedStandardField, \
            OriginCountry, RecordUsersField, RecordStateField, RecordSelectField, RecordMultipleField
        try:
            RecordTemplate.objects.first()
            RecordStandardField.objects.first()
            RecordEncryptedStandardField.objects.first()
            OriginCountry.objects.first()
            RecordUsersField.objects.first()
            RecordStateField.objects.first()
            RecordSelectField.objects.first()
            RecordMultipleField.objects.first()
        except (OperationalError, ProgrammingError):
            # the needed tables don't exist
            return
        for rlc in Rlc.objects.all():
            if rlc.recordtemplates.count() == 0:
                create_default_record_template(rlc)
