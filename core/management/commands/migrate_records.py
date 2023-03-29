import time

from django.core.management.base import BaseCommand
from django.db import transaction

from core.data_sheets.models.record import Record
from core.folders.domain.value_objects.folder_item import FolderItem
from core.folders.models import FoldersFolder
from core.records.models.record import RecordsRecord
from core.rlc.models.org import Org


class Command(BaseCommand):
    def handle(self, *args, **options):
        t1 = time.time()
        # folder_repository = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))

        sheets = list(
            Record.objects.exclude(folder_uuid=None)
            .select_related("template", "template__rlc")
            .prefetch_related("standard_entries", "standard_entries__field")
            .order_by("id")
        )

        folders = list(FoldersFolder.objects.all())
        folders = {folder.uuid: folder for folder in folders}

        created_records_inside_folders_uuids = list(
            RecordsRecord.objects.values_list("folder_uuid", flat=True)
        )

        name_difference = []

        for org in list(Org.objects.all().order_by("id")):
            self.stdout.write(f"Working on org: {org.id}")
            # folders = folder_repository.get_dict(org.pk)

            for sheet in sheets:
                if sheet.template.rlc_id != org.id:
                    continue

                # if sheet.id > 500:
                #     break

                self.stdout.write(f"Working on sheet: {sheet.id}")

                folder: FoldersFolder = folders[sheet.folder_uuid]

                if folder.uuid not in created_records_inside_folders_uuids:
                    record = RecordsRecord(
                        name=folder.name,
                        org=sheet.template.rlc,
                        folder_uuid=folder.uuid,
                        created=sheet.created,
                        updated=sheet.updated,
                    )
                    folder.restricted = True
                    folder_item = FolderItem.create_from_item(record)
                    length = len(folder.items)
                    folder.items.append(folder_item.as_dict())
                    assert len(folder.items) == length + 1

                    created_records_inside_folders_uuids.append(folder.uuid)

                    with transaction.atomic():
                        folder.save(update_fields=["restricted", "items"])
                        record.save()

                    if record.name != sheet.identifier or record.name != folder.name:
                        name_difference.append(
                            (record.name, sheet.identifier, folder.name)
                        )

                    self.stdout.write(
                        f"Record '{record.name}' created out of sheet '{sheet.identifier}' and folder saved"
                    )

                else:
                    self.stdout.write("Folder already contains a record")

        t2 = time.time()

        for diff in name_difference:
            self.stdout.write(
                f"Name difference between (Record, Sheet, Folder): {diff}"
            )

        self.stdout.write(f"Done in {t2 - t1} seconds")


# records: 4209
# timing (500): 50 seconds
# timing (500): 45 seconds
# timing (100): 50 seconds
# timing (100): 41 seconds
# timing (100): 40 seconds
# timing (100): 40 seconds
# timing (100): 10 seconds
# timing (500): 10 seconds
# timing (ALL): 11 seconds
