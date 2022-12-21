from django.core.management.base import BaseCommand

from core.files_new.models import EncryptedRecordDocument


class Command(BaseCommand):
    def handle(self, *args, **options):
        d_list = []
        for d in list(
            EncryptedRecordDocument.objects.select_related(
                "record", "record__template"
            ).order_by("id")
        ):
            if d.record:
                d.org_id = d.record.template.rlc_id
                d_list.append(d)
        EncryptedRecordDocument.objects.bulk_update(d_list, ["org_id"])
