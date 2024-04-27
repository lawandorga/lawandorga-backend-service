from django.core.management.base import BaseCommand

from core.data_sheets.models.data_sheet import DataSheet
from core.records.models.record import RecordsRecord

from seedwork.functional import group_by


class Command(BaseCommand):
    def handle(self, *args, **options):
        records = list(RecordsRecord.objects.all())
        sheetsl = list(DataSheet.objects.all())
        sheets = group_by(sheetsl, lambda x: x.folder_uuid)
        for r in records:
            r.set_attributes(sheets.get(r.folder_uuid, []))
        RecordsRecord.objects.bulk_update(records, ["attributes"])
