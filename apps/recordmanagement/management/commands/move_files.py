from apps.recordmanagement.models import EncryptedRecordDocument
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Attaches the files to the new record."

    def handle(self, *args, **options):
        for file in EncryptedRecordDocument.objects.all():
            new_record = file.old_record.record
            file.record = new_record
            file.save()
