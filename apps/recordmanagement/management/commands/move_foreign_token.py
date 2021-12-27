from apps.recordmanagement.models import RecordTemplate, RecordEncryptedStandardField, Record, \
    RecordEncryptedStandardEntry
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Moves the forgotten token."

    def handle(self, *args, **options):
        with transaction.atomic():
            for template in RecordTemplate.objects.all():
                RecordEncryptedStandardField.objects.get_or_create(template=template, order=135, name='Foreign Token')
        for record in Record.objects.all().select_related('old_record', 'template'):
            print(record.id)
            if record.old_record and record.old_record.foreign_token:
                field = RecordEncryptedStandardField.objects.get(template__rlc=record.template.rlc,
                                                                 name='Foreign Token')
                RecordEncryptedStandardEntry.objects.get_or_create(record=record, field=field,
                                                                   value=record.old_record.foreign_token)
