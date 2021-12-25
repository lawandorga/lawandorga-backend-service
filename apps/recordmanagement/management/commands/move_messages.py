from apps.recordmanagement.models import EncryptedRecordMessage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Attaches the messages to the new record."

    def handle(self, *args, **options):
        for message in EncryptedRecordMessage.objects.all():
            new_record = message.old_record.record
            message.record = new_record
            message.save()
