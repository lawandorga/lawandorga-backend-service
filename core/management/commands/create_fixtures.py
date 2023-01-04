from django.core.management.base import BaseCommand

from core.fixtures import create


class Command(BaseCommand):
    def handle(self, *args, **options):
        create()
