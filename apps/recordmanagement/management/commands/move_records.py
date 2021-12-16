from django.db import transaction

from apps.recordmanagement.models import Record, RecordStandardEntry, RecordStandardField, RecordUsersField, RecordStateField, \
    RecordEncryptedStandardField, RecordUsersEntry, RecordStateEntry, RecordEncryptedSelectField, RecordEncryptedSelectEntry, RecordSelectField, \
    RecordSelectEntry, RecordEncryptedStandardEntry, EncryptedRecord
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Moves the records to the new format."

    def handle(self, *args, **options):
        for record in EncryptedRecord.objects.all():
            move_record(record)


def move_record(old_record):
    with transaction.atomic():
        template = old_record.from_rlc.recordtemplates.first()
        record = Record.objects.create(template=template, old_record=old_record)
        # record entries
        #
        field = RecordStandardField.objects.get(template=template, name='First contact date')
        if old_record.first_contact_date:
            RecordStandardEntry.objects.create(record=record, field=field, text=old_record.first_contact_date)
        #
        field = RecordStandardField.objects.get(template=template, name='Last contact date')
        if old_record.last_contact_date:
            RecordStandardEntry.objects.create(record=record, field=field, text=old_record.last_contact_date)
        #
        field = RecordStandardField.objects.get(template=template, name='First consultation')
        if old_record.first_consultation:
            RecordStandardEntry.objects.create(record=record, field=field, text=old_record.first_consultation)
        #
        field = RecordStandardField.objects.get(template=template, name='Official Note')
        if old_record.official_note:
            RecordStandardEntry.objects.create(record=record, field=field, text=old_record.official_note)
        #
        field = RecordUsersField.objects.get(template=template, name='Consultants')
        if old_record.working_on_record:
            entry = RecordUsersEntry.objects.create(record=record, field=field)
            entry.users.set(old_record.working_on_record.all())
        #
        field = RecordSelectField.objects.get(template=template, name='Tags')
        if old_record.tags.values_list('name', flat=True):
            tags = list(old_record.tags.values_list('name', flat=True))
            if not tags:
                tags = []
            RecordSelectEntry.objects.create(record=record, field=field, value=tags)
        #
        field = RecordStateField.objects.get(template=template, name='State')
        if old_record.get_state_display().capitalize():
            RecordStateEntry.objects.create(record=record, field=field, state=old_record.get_state_display().capitalize())
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Note')
        if old_record.note:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.note)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Consultant Team')
        if old_record.consultant_team:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.consultant_team)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Lawyer')
        if old_record.lawyer:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.lawyer)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Related Persons')
        if old_record.related_persons:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.related_persons)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Contact')
        if old_record.contact:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.contact)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='BAMF Token')
        if old_record.bamf_token:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.bamf_token)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='First Correspondence')
        if old_record.first_correspondence:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.first_correspondence)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Circumstances')
        if old_record.circumstances:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.circumstances)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Next Steps')
        if old_record.next_steps:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.next_steps)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Status described')
        if old_record.status_described:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.status_described)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Additional facts')
        if old_record.additional_facts:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.additional_facts)
        # client entries
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Client name')
        if old_record.client.name:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.client.name)
        #
        field = RecordStandardField.objects.get(template=template, name='Birthday')
        if old_record.client.birthday:
            RecordStandardEntry.objects.create(record=record, field=field, text=old_record.client.birthday)
        #
        field = RecordSelectField.objects.get(template=template, name='Origin Country')
        if old_record.client.origin_country:
            value = [old_record.client.origin_country.name]
            RecordSelectEntry.objects.create(record=record, field=field, value=value)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Phone')
        if old_record.client.phone_number:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.client.phone_number)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Client Note')
        if old_record.client.note:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, text=old_record.client.note)
