from django.core.management.base import BaseCommand
from django.db import transaction

from core.folders.models import FOL_ClosureTable, FOL_Folder
from core.org.models.org import Org


class Command(BaseCommand):
    help = "Fix Closures"

    def handle(self, *args, **options):
        for org in Org.objects.order_by("pk"):
            self.stdout.write(f"Org {org.pk}")
            for f in FOL_Folder.objects.filter(org_id=org.pk, deleted=False).order_by(
                "pk"
            ):
                closures = FOL_ClosureTable.objects.filter(child_id=f.pk)
                parent = f._parent
                expected_parent_ids = []
                while parent is not None:
                    expected_parent_ids.append(parent.pk)
                    parent = parent._parent
                actual_parent_ids = [c.parent_id for c in closures]
                if set(expected_parent_ids) != set(actual_parent_ids):
                    self.stdout.write(
                        f"FIXING {f.pk}: expected {expected_parent_ids}, got {actual_parent_ids}"
                    )
                    with transaction.atomic():
                        FOL_ClosureTable.objects.filter(child_id=f.pk).delete()
                        new_closures = [
                            FOL_ClosureTable(parent_id=pid, child_id=f.pk)
                            for pid in expected_parent_ids
                        ]
                        FOL_ClosureTable.objects.bulk_create(new_closures)
