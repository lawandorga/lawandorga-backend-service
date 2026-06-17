from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.data_sheets.models.data_sheet import DataSheetStandardEntry
from core.folders.models import FOL_Folder
from core.folders.use_cases.folder import rename_item_in_folder
from core.org.models.org import Org
from core.records.models.record import RecordsRecord
from core.seedwork.message_layer import MessageBusActor


class Command(BaseCommand):
    help = (
        "Fixes record names that are '-' by copying a Data Sheet field value (default: field 'token') "
        "from a DataSheet in the same folder. Updates both the record row and the folder's items JSON."
    )

    def add_arguments(self, parser) -> None:  # type: ignore[override]
        parser.add_argument(
            "--org-name",
            default="Dummy RLC",
            help="Org/RLC name to operate on (default: 'Dummy RLC')",
        )
        parser.add_argument(
            "--field-name",
            default="token",
            help="DataSheet standard field name to copy from (default: 'token')",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write changes, only print what would happen",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional max number of records to process (0 = no limit)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print per-record decisions",
        )

    def handle(self, *args: Any, **options: Any) -> None:  # type: ignore[override]
        org_name: str = options["org_name"]
        field_name: str = options["field_name"]
        dry_run: bool = options["dry_run"]
        limit: int = options["limit"]
        verbose: bool = options["verbose"]

        try:
            org = Org.objects.get(name=org_name)
        except Org.DoesNotExist as exc:
            similar = list(
                Org.objects.filter(name__icontains=org_name)
                .order_by("name")
                .values_list("name", flat=True)[:20]
            )
            hint = ""
            if similar:
                hint = f" Similar org names: {', '.join(similar)}"
            raise CommandError(f"Org not found: '{org_name}'.{hint}") from exc

        records_qs = RecordsRecord.objects.filter(org=org).order_by("id")
        if limit and limit > 0:
            records_qs = records_qs[:limit]

        folder_uuids = list(records_qs.values_list("folder_uuid", flat=True))
        if not folder_uuids:
            self.stdout.write("No matching records found. Nothing to do.")
            return

        token_entries = (
            DataSheetStandardEntry.objects.filter(
                record__template__org=org,
                record__folder_uuid__in=folder_uuids,
                field__name__iexact=field_name,
            )
            .exclude(value__isnull=True)
            .values_list("record__folder_uuid", "value")
        )

        token_by_folder: dict = defaultdict(set)
        for folder_uuid, value in token_entries.iterator(chunk_size=2000):
            if value is None:
                continue
            token = str(value).strip()
            if len(token) < 4:
                continue
            token_by_folder[folder_uuid].add(token)

        name_max_len = RecordsRecord._meta.get_field("name").max_length
        actor = MessageBusActor(org.pk)

        stats = {
            "candidates": 0,
            "updated": 0,
            "skipped_no_token": 0,
            "skipped_multi_token": 0,
            "skipped_too_long": 0,
        }

        self.stdout.write(
            f"Org='{org.name}': scanning {len(folder_uuids)} records (dry_run={dry_run})."
        )

        for record in records_qs.iterator(chunk_size=500):
            stats["candidates"] += 1
            candidates = token_by_folder.get(record.folder_uuid, set())

            if not candidates:
                stats["skipped_no_token"] += 1
                if verbose:
                    self.stdout.write(
                        f"SKIP record_id={record.pk}: no '{field_name}' value in folder {record.folder_uuid}"
                    )
                continue

            if len(candidates) > 1:
                stats["skipped_multi_token"] += 1
                if verbose:
                    self.stdout.write(
                        f"SKIP record_id={record.pk}: multiple '{field_name}' values in folder {record.folder_uuid}: {sorted(candidates)}"
                    )
                continue

            new_name = next(iter(candidates))
            if name_max_len is not None and len(new_name) > int(name_max_len):
                stats["skipped_too_long"] += 1
                if verbose:
                    self.stdout.write(
                        f"SKIP record_id={record.pk}: token too long ({len(new_name)}>{name_max_len})"
                    )
                continue

            if verbose or dry_run:
                self.stdout.write(
                    f"{'DRY' if dry_run else 'DO '} record_id={record.pk}: '{record.name}' -> '{new_name}'"
                )

            if dry_run:
                continue

            folder = FOL_Folder.objects.get(org=org, uuid=record.folder_uuid)

            if len(folder.name) > 4:
                continue

            with transaction.atomic():
                record.name = new_name
                record.save(update_fields=["name"])
                folder.name = new_name
                folder.save(update_fields=["name"])
                rename_item_in_folder(
                    actor,
                    record.REPOSITORY,
                    new_name,
                    record.uuid,
                    record.folder_uuid,
                )

            stats["updated"] += 1

        self.stdout.write(
            "Done. "
            f"candidates={stats['candidates']} updated={stats['updated']} "
            f"skipped_no_token={stats['skipped_no_token']} "
            f"skipped_multi_token={stats['skipped_multi_token']} "
            f"skipped_too_long={stats['skipped_too_long']}"
        )
