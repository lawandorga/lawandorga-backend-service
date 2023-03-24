from django.core.management import BaseCommand

from core.data_sheets.models import RecordAccess, RecordDeletion


class Command(BaseCommand):
    def handle(self, *args, **options):
        d1 = RecordDeletion.objects.all()
        d2 = list(d1)
        for d in d2:
            if d.requested_by:
                d.requestor = d.requested_by.rlc_user
            if d.processed_by:
                d.processor = d.processed_by.rlc_user
        RecordDeletion.objects.bulk_update(d2, ["requestor", "processor"])

        a1 = RecordAccess.objects.all()
        a2 = list(a1)
        for a in a2:
            if a.requested_by:
                a.requestor = a.requested_by.rlc_user
            if a.processed_by:
                a.processor = a.processed_by.rlc_user
        RecordAccess.objects.bulk_update(a2, ["requestor", "processor"])
