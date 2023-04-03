from uuid import uuid4
from django.core.management.base import BaseCommand

from core.data_sheets.models.template import RecordField
from django.db import transaction


class Command(BaseCommand):
    help = "Migrates Data"

    def handle(self, *args, **options):
        with transaction.atomic():
            for subclass in RecordField.__subclasses__():
                for field in subclass.objects.all():
                    field.uuid = uuid4()
                    field.save()
