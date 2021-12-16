from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Moves the records to the new format."

    def handle(self, *args, **options):
        pass
