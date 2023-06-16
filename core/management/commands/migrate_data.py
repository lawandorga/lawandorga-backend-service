from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Migrates Data"

    def handle(self, *args, **options):
        pass
