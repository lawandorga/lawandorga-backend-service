from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

from core.management.commands.delete_rlc import force_delete
from core.management.commands.empty_rlc import force_empty
from core.models import Org
from core.tests.example_data import create

DUMMY_ORG_NAME = "Dummy RLC"
DUMMY_USER_EMAIL = "dummy@law-orga.de"
NEIGHBOURHOOD_ORG_NAME = "Neighbourhood RLC"


class Command(BaseCommand):
    help = (
        "Deletes the dummy org (Dummy RLC) and the neighbourhood org (Neighbourhood RLC) and recreates dummy data. "
        "Only affects those orgs; other orgs are left untouched."
    )

    def handle(self, *args, **options):

        dummy_org = Org.objects.filter(name=DUMMY_ORG_NAME).first()
        neighbourhood_org = Org.objects.filter(name=NEIGHBOURHOOD_ORG_NAME).first()

        if dummy_org is not None:
            force_empty(dummy_org)
            force_delete(dummy_org)

        if neighbourhood_org is not None:
            force_empty(neighbourhood_org)
            force_delete(neighbourhood_org)

        settings._wrapped.TESTING = True

        create()

        self.stdout.write("Dummy data regenerated.")
