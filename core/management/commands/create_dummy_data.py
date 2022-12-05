from django.conf import settings
from django.core.management.base import BaseCommand

from core.rlc.tests.example_data import create


class Command(BaseCommand):
    help = "Populates database for deployment environment."

    def handle(self, *args, **options):
        # this is hacky but it seems fine at this place. it is needed to
        # be able to get the private_key of the dummy user to encrypt
        # the created records
        settings._wrapped.TESTING = True
        create()
