from apps.recordmanagement.models import Record, RecordStandardEntry, RecordStandardField, RecordUsersField, \
    RecordStateField, RecordEncryptedStandardField, RecordUsersEntry, RecordStateEntry, RecordSelectField, \
    RecordSelectEntry, RecordEncryptedStandardEntry, EncryptedRecord, RecordEncryption, RecordEncryptionNew, \
    RecordMultipleField, RecordMultipleEntry
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Moves the records to the new format."

    def handle(self, *args, **options):
        for record in EncryptedRecord.objects.all():
            if not hasattr(record, 'record'):
                move_record(record)
            test_record(record)


def move_encryptions(old_record, new_record):
    for enc in RecordEncryption.objects.filter(record=old_record):
        RecordEncryptionNew.objects.create(
            user=enc.user,
            record=new_record,
            key=enc.encrypted_key,
        )


def move_record(old_record):
    with transaction.atomic():
        template = old_record.from_rlc.recordtemplates.first()
        record = Record.objects.create(template=template, old_record=old_record)
        # create new encryption
        move_encryptions(old_record, record)
        # record entries
        #
        field = RecordStandardField.objects.get(template=template, name='Token')
        if old_record.record_token:
            RecordStandardEntry.objects.create(record=record, field=field, value=old_record.record_token)
        #
        field = RecordStandardField.objects.get(template=template, name='First contact date')
        if old_record.first_contact_date:
            RecordStandardEntry.objects.create(record=record, field=field, value=old_record.first_contact_date)
        #
        field = RecordStandardField.objects.get(template=template, name='Last contact date')
        if old_record.last_contact_date:
            RecordStandardEntry.objects.create(record=record, field=field, value=old_record.last_contact_date)
        #
        field = RecordStandardField.objects.get(template=template, name='First consultation')
        if old_record.first_consultation:
            RecordStandardEntry.objects.create(record=record, field=field, value=old_record.first_consultation)
        #
        field = RecordStandardField.objects.get(template=template, name='Official Note')
        if old_record.official_note:
            RecordStandardEntry.objects.create(record=record, field=field, value=old_record.official_note)
        #
        field = RecordUsersField.objects.get(template=template, name='Consultants')
        if old_record.working_on_record:
            entry = RecordUsersEntry.objects.create(record=record, field=field)
            entry.value.set(old_record.working_on_record.all())
        #
        field = RecordMultipleField.objects.get(template=template, name='Tags')
        if old_record.tags.values_list('name', flat=True):
            tags = list(old_record.tags.values_list('name', flat=True))
            if not tags:
                tags = []
            RecordMultipleEntry.objects.create(record=record, field=field, value=tags)
        #
        field = RecordStateField.objects.get(template=template, name='State')
        if old_record.get_state_display().capitalize():
            RecordStateEntry.objects.create(record=record, field=field,
                                            value=old_record.get_state_display().capitalize())
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Note')
        if old_record.note:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.note)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Consultant Team')
        if old_record.consultant_team:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.consultant_team)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Lawyer')
        if old_record.lawyer:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.lawyer)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Related Persons')
        if old_record.related_persons:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.related_persons)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Contact')
        if old_record.contact:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.contact)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='BAMF Token')
        if old_record.bamf_token:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.bamf_token)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='First Correspondence')
        if old_record.first_correspondence:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field,
                                                        value=old_record.first_correspondence)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Circumstances')
        if old_record.circumstances:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.circumstances)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Next Steps')
        if old_record.next_steps:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.next_steps)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Status described')
        if old_record.status_described:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.status_described)
        #
        field = RecordEncryptedStandardField.objects.get(template=template, name='Additional facts')
        if old_record.additional_facts:
            RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.additional_facts)
        # client entries
        record.old_client = old_record.client
        record.save()
        #
        # field = RecordEncryptedStandardField.objects.get(template=template, name='Client name')
        # if old_record.client.name:
        #     RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.client.name)
        #
        field = RecordStandardField.objects.get(template=template, name='Birthday')
        if old_record.client.birthday:
            RecordStandardEntry.objects.create(record=record, field=field, value=old_record.client.birthday)
        #
        field = RecordSelectField.objects.get(template=template, name='Origin Country')
        if old_record.client.origin_country:
            value = old_record.client.origin_country.name
            RecordSelectEntry.objects.create(record=record, field=field, value=value)
        #
        # field = RecordEncryptedStandardField.objects.get(template=template, name='Phone')
        # if old_record.client.phone_number:
        #     RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.client.phone_number)
        # #
        # field = RecordEncryptedStandardField.objects.get(template=template, name='Client Note')
        # if old_record.client.note:
        #     RecordEncryptedStandardEntry.objects.create(record=record, field=field, value=old_record.client.note)


def test_record(record):
    old_record = record
    new_record = Record.objects.get(old_record=record)
    template = new_record.template
    field = RecordStandardField.objects.get(template=template, name='First contact date')
    if old_record.first_contact_date:
        entry = RecordStandardEntry.objects.get(record=new_record, field=field)
        assert str(old_record.first_contact_date) == entry.value, '{} != {}'.format(old_record.first_contact_date,
                                                                                    entry.value)
    #
    field = RecordStandardField.objects.get(template=template, name='Last contact date')
    if old_record.last_contact_date:
        entry = RecordStandardEntry.objects.get(record=new_record, field=field)
        assert str(old_record.last_contact_date) == entry.value, '{} != {}'.format(old_record.last_contact_date,
                                                                                   entry.value)
    #
    field = RecordStandardField.objects.get(template=template, name='First consultation')
    if old_record.first_consultation:
        entry = RecordStandardEntry.objects.get(record=new_record, field=field)
        assert str(old_record.first_consultation) == entry.value, '{} != {}'.format(old_record.first_consultation,
                                                                                    entry.value)
    #
    field = RecordStandardField.objects.get(template=template, name='Official Note')
    if old_record.official_note:
        entry = RecordStandardEntry.objects.get(record=new_record, field=field)
        assert str(old_record.official_note) == entry.value, '{} != {}'.format(old_record.official_note, entry.value)
    #
    field = RecordUsersField.objects.get(template=template, name='Consultants')
    if old_record.working_on_record:
        entry = RecordUsersEntry.objects.get(record=new_record, field=field)
        assert list(old_record.working_on_record.values_list('pk', flat=True)) == list(
            entry.value.values_list('pk', flat=True)), \
            '{} != {}'.format(list(old_record.working_on_record.values_list('pk', flat=True)),
                              list(entry.value.values_list('pk', flat=True)))
    #
    field = RecordMultipleField.objects.get(template=template, name='Tags')
    if old_record.tags.values_list('name', flat=True):
        entry = RecordMultipleEntry.objects.get(record=new_record, field=field)
        assert list(old_record.tags.values_list('name', flat=True)) == entry.value, \
            '{} != {}'.format(list(old_record.tags.values_list('name', flat=True)), entry.value)
    #
    field = RecordStateField.objects.get(template=template, name='State')
    if old_record.get_state_display().capitalize():
        entry = RecordStateEntry.objects.get(record=new_record, field=field)
        assert str(old_record.get_state_display().capitalize()) == entry.value, '{} != {}'.format(
            old_record.get_state_display, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Note')
    if old_record.note:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert old_record.note == entry.value, '{} != {}'.format(old_record.note, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Consultant Team')
    if old_record.consultant_team:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert old_record.consultant_team == entry.value, '{} != {}'.format(old_record.consultant_team,
                                                                            entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Lawyer')
    if old_record.lawyer:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert old_record.lawyer == entry.value, '{} != {}'.format(old_record.lawyer, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Related Persons')
    if old_record.related_persons:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert old_record.related_persons == entry.value, '{} != {}'.format(old_record.related_persons,
                                                                            entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Contact')
    if old_record.contact:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.contact) == entry.value, '{} != {}'.format(old_record.contact, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='BAMF Token')
    if old_record.bamf_token:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.bamf_token) == entry.value, '{} != {}'.format(old_record.bamf_token, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='First Correspondence')
    if old_record.first_correspondence:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.first_correspondence) == entry.value, '{} != {}'.format(old_record.first_correspondence,
                                                                                   entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Circumstances')
    if old_record.circumstances:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.circumstances) == entry.value, '{} != {}'.format(old_record.circumstances, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Next Steps')
    if old_record.next_steps:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.next_steps) == entry.value, '{} != {}'.format(old_record.next_steps, entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Status described')
    if old_record.status_described:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.status_described) == entry.value, '{} != {}'.format(old_record.status_described,
                                                                               entry.value)
    #
    field = RecordEncryptedStandardField.objects.get(template=template, name='Additional facts')
    if old_record.additional_facts:
        entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
        assert (old_record.additional_facts) == entry.value, '{} != {}'.format(old_record.additional_facts,
                                                                               entry.value)
    # client entries
    assert new_record.old_client == old_record.client, '{} != {}'.format(record.old_client.pk, old_record.client.pk)
    #
    # field = RecordEncryptedStandardField.objects.get(template=template, name='Client name')
    # if old_record.client.name:
    #     entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
    #     assert old_record.client.name == entry.value, '{} != {}'.format(old_record.client.name, entry.value)
    # #
    field = RecordStandardField.objects.get(template=template, name='Birthday')
    if old_record.client.birthday:
        entry = RecordStandardEntry.objects.get(record=new_record, field=field)
        assert str(old_record.client.birthday) == entry.value, '{} != {}'.format(old_record.client.birthday,
                                                                                 entry.value)
    # #
    field = RecordSelectField.objects.get(template=template, name='Origin Country')
    if old_record.client.origin_country:
        entry = RecordSelectEntry.objects.get(record=new_record, field=field)
        assert str(old_record.client.origin_country.name) == entry.value, \
            '{} != {}'.format(old_record.client.origin_country.name, entry.value)
    # #
    # field = RecordEncryptedStandardField.objects.get(template=template, name='Phone')
    # if old_record.client.phone_number:
    #     entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
    #     assert old_record.client.phone_number == entry.value, '{} != {}'.format(old_record.client.phone_number,
    #                                                                             entry.value)
    # #
    # field = RecordEncryptedStandardField.objects.get(template=template, name='Client Note')
    # if old_record.client.note:
    #     entry = RecordEncryptedStandardEntry.objects.get(record=new_record, field=field)
    #     assert old_record.client.note == entry.value, '{} != {}'.format(old_record.client.note, entry.value)
