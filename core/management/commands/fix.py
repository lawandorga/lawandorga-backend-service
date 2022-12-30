from django.core.management import BaseCommand

from core.messages.models import EncryptedRecordMessage


class Command(BaseCommand):
    def handle(self, *args, **options):
        messages = list(
            EncryptedRecordMessage.objects.all().select_related(
                "record", "record__template"
            )
        )
        for message in messages:
            message.org_id = message.record.template.rlc_id
        EncryptedRecordMessage.objects.bulk_update(messages, ["org_id"])
