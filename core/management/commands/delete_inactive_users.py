import csv
from datetime import datetime, timedelta
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models import Q

from core.auth.models.user import UserProfile


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            help=(
                "Path to write a CSV report of successfully deleted users. "
                "Defaults to ./deleted_inactive_users.csv"
            ),
        )

    def handle(self, *args, **options):
        inactivity_years = 3
        three_years_ago = datetime(2026, 1, 14) - timedelta(days=365 * inactivity_years)
        inactive_users = UserProfile.objects.filter(
            Q(last_login__lt=three_years_ago)
            | ((Q(last_login__isnull=True) & Q(created__lt=three_years_ago)))
        ).order_by("-pk")
        self.stdout.write(f"Found {inactive_users.count()} inactive users.")
        input("Press Enter to delete them...")

        output_path = options.get("output")
        if not output_path:
            output_path = "deleted_inactive_users.csv"
        output_path = Path(output_path).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        for u in list(inactive_users):
            self.stdout.write(
                f"{u.pk} - {u.email} - {u.last_login.isoformat() if u.last_login else 'Never'} - {u.created.isoformat()}"
            )
            u.delete()
            file_exists_and_has_content = (
                output_path.exists() and output_path.stat().st_size > 0
            )
            file_mode = "a" if file_exists_and_has_content else "w"
            with output_path.open(file_mode, newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["pk", "email", "last_login", "created", "deleted_at"],
                )
                if not file_exists_and_has_content:
                    writer.writeheader()
                writer.writerow(
                    {
                        "pk": u.pk,
                        "email": u.email,
                        "last_login": u.last_login.isoformat() if u.last_login else "",
                        "created": u.created.isoformat() if u.created else "",
                        "deleted_at": datetime.now().isoformat(),
                    }
                )
        self.stdout.write(f"Wrote deleted users report to: {output_path}")
