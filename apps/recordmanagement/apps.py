from django.apps import AppConfig
from django.db import OperationalError


class RecordmanagementConfig(AppConfig):
    name = "apps.recordmanagement"

    def ready(self):
        from apps.recordmanagement.fixtures import create_default_record_template
        from apps.api.models import Rlc
        from apps.recordmanagement.models import RecordTemplate
        try:
            list([RecordTemplate.objects.first()])
        except OperationalError:
            # the needed tables don't exist
            return
        for rlc in Rlc.objects.all():
            if rlc.recordtemplates.count() == 0:
                create_default_record_template(rlc)
