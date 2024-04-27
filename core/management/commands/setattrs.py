from django.core.management.base import BaseCommand

from core.data_sheets.models.data_sheet import DataSheet
from core.records.models.record import RecordsRecord

from seedwork.functional import create_chunks, group_by


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("getting records")
        records = list(RecordsRecord.objects.all().order_by("id"))
        self.stdout.write("getting sheets")
        sheetsl = list(
            DataSheet.objects.all()
            .order_by("id")
            .prefetch_related(*DataSheet.UNENCRYPTED_PREFETCH_RELATED)
        )
        self.stdout.write("grouping sheets")
        sheets = group_by(sheetsl, lambda x: x.folder_uuid)
        for r in records:
            self.stdout.write(f"processing record {r.pk}")
            r.set_attributes(sheets.get(r.folder_uuid, []))
        for chunk in create_chunks(records, 1000):
            self.stdout.write(f"updating {len(chunk)} records")
            RecordsRecord.objects.bulk_update(chunk, ["attributes"])
