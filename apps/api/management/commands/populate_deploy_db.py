from django.core.management.base import BaseCommand
from .commands import populate_deploy_db


class Command(BaseCommand):
    help = "populates database for deployment environment"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        populate_deploy_db()
