from django.core.management.base import BaseCommand

from core.cronjobs import CronjobWarehouse


class Command(BaseCommand):
    help = "Runs cronjobs."

    def handle(self, *args, **options):
        results = CronjobWarehouse.run_cronjobs()
        self.stdout.write("\n".join(results))
