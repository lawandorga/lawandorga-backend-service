import time

from django.core.management.base import BaseCommand

from core.folders.models import FoldersFolder


class Command(BaseCommand):
    def handle(self, *args, **options):
        t1 = time.time()

        folders = list(FoldersFolder.objects.filter())

        for folder in folders:
            contains_files = False
            contains_record = False
            for item in folder.items:
                if item["repository"] == "FILE":
                    contains_files = True
                if item["repository"] == "RECORDS_RECORD":
                    contains_record = True
            if contains_files and not contains_record:
                self.stdout.write(
                    f"Folder '{folder.name}' contains files but no records."
                )

        t2 = time.time()

        self.stdout.write(f"Done in {t2 - t1} seconds.")
