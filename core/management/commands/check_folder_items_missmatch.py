import time
from uuid import UUID

from django.core.management.base import BaseCommand

from core.data_sheets.models.record import Record
from core.folders.models import FoldersFolder


class Command(BaseCommand):
    def handle(self, *args, **options):
        t1 = time.time()

        folders = list(FoldersFolder.objects.all())
        records = list(
            Record.objects.exclude(folder_uuid=None)
            .all()
            .prefetch_related("standard_entries", "standard_entries__field")
            .select_related("template", "template__rlc")
            .order_by("template__rlc_id")
        )

        self.stdout.write("Querying done. Checking...")

        for record in records:
            errors = []
            for folder in folders:
                for item in folder.items:
                    if (
                        UUID(item["uuid"]) == record.uuid
                        and folder.uuid != record.folder_uuid
                    ):
                        errors.append(folder)
            if len(errors):
                self.stdout.write(
                    f"Record '{record.identifier}' is in {len(errors)} error folders. Fixing..."
                )
                for folder in errors:
                    folder.items = [
                        item
                        for item in folder.items
                        if UUID(item["uuid"]) != record.uuid
                    ]
                    folder.save(update_fields=["items"])
                self.stdout.write(f"Folder '{folder.name}' fixed.")

        t2 = time.time()

        self.stdout.write(f"Done in {t2 - t1} seconds.")
