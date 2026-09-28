from collections import defaultdict
from collections.abc import Iterator

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from core.calendar.models import CalendarEventAttachment
from core.collab.models import Letterhead
from core.data_sheets.models import DataSheetEncryptedFileEntry
from core.files.models.file import File
from core.files_new.models.file import EncryptedRecordDocument
from core.mail_imports.models.mail_import import MailAttachment
from core.org.models import Org
from core.questionnaires.models import QuestionnaireTemplateFile
from core.seedwork.storage_folders import get_storage_base_files_folder
from core.upload.models.upload import UploadFile


def format_size(size_in_bytes: int) -> str:
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(size_in_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024

    raise AssertionError("unreachable")


class Command(BaseCommand):
    help = "Show S3 storage usage for each organization."

    def add_arguments(self, parser) -> None:  # type: ignore[override]
        parser.add_argument(
            "--org-id",
            type=int,
            help="Only report storage for this organization.",
        )

    def handle(self, *args, **options) -> None:
        orgs = Org.objects.order_by("id")
        if org_id := options["org_id"]:
            orgs = orgs.filter(pk=org_id)

        orgs_by_id = {org.pk: org for org in orgs}
        if not orgs_by_id:
            raise CommandError("No organizations match the supplied filter.")

        storage = default_storage
        if not hasattr(storage, "bucket"):
            raise CommandError("The configured storage backend is not S3.")

        object_org_ids = self.get_object_org_ids(orgs_by_id)
        totals: dict[int, int] = defaultdict(int)
        object_counts: dict[int, int] = defaultdict(int)

        for key, size in self.iter_objects(storage):
            org_id = object_org_ids.get(key) or self.get_legacy_org_id(key, orgs_by_id)
            if org_id is not None:
                totals[org_id] += size
                object_counts[org_id] += 1

        self.stdout.write("ID\tOrganization\tObjects\tBytes\tStorage")
        for org_id, org in orgs_by_id.items():
            self.stdout.write(
                f"{org_id}\t{org.name}\t{object_counts[org_id]}\t"
                f"{totals[org_id]}\t{format_size(totals[org_id])}"
            )

    def get_object_org_ids(self, orgs_by_id: dict[int, Org]) -> dict[str, int]:
        org_ids = orgs_by_id.keys()
        object_org_ids = {
            f"{location}.enc": org_id
            for org_id, location in EncryptedRecordDocument.objects.filter(
                org_id__in=org_ids
            ).values_list("org_id", "location")
        }
        file_fields = (
            CalendarEventAttachment.objects.filter(
                event__creator__org_id__in=org_ids
            ).values_list("event__creator__org_id", "file"),
            Letterhead.objects.filter(org_id__in=org_ids).values_list("org_id", "logo"),
            DataSheetEncryptedFileEntry.objects.filter(
                record__template__org_id__in=org_ids
            ).values_list("record__template__org_id", "file"),
            File.objects.filter(folder__rlc_id__in=org_ids).values_list(
                "folder__rlc_id", "file"
            ),
            MailAttachment.objects.filter(mail_import__org_id__in=org_ids).values_list(
                "mail_import__org_id", "content"
            ),
            QuestionnaireTemplateFile.objects.filter(
                questionnaire__org_id__in=org_ids
            ).values_list("questionnaire__org_id", "file"),
            UploadFile.objects.filter(link__org_id__in=org_ids).values_list(
                "link__org_id", "file"
            ),
        )

        for file_field in file_fields:
            for org_id, key in file_field:
                if key:
                    object_org_ids[key] = org_id

        return object_org_ids

    @staticmethod
    def get_legacy_org_id(key: str, orgs_by_id: dict[int, Org]) -> int | None:
        for org_id in orgs_by_id:
            if key.startswith(get_storage_base_files_folder(org_id)):
                return org_id
        return None

    @staticmethod
    def iter_objects(storage) -> Iterator[tuple[str, int]]:
        paginator = storage.bucket.meta.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=storage.bucket_name):
            for item in page.get("Contents", []):
                yield item["Key"], item["Size"]
