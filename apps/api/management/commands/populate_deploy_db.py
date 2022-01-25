from apps.api.management.commands.fixtures import Fixtures
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "populates database for deployment environment"

    def handle(self, *args, **options):
        Fixtures.create_real_permissions_no_duplicates()
        Fixtures.create_real_collab_permissions()
