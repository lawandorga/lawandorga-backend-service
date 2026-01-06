from django.core.management.base import BaseCommand

from core.tests.fixtures import create


class Command(BaseCommand):
    def handle(self, *args, **options):
        create()
