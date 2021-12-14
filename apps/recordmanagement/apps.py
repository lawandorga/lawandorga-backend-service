from apps.recordmanagement.fixtures import create_default_record_template
from apps.api.models import Rlc
from django.apps import AppConfig


class RecordmanagementConfig(AppConfig):
    name = "apps.recordmanagement"

    def ready(self):
        for rlc in Rlc.objects.all():
            if rlc.recordtemplates.count() == 0:
                create_default_record_template(rlc)
