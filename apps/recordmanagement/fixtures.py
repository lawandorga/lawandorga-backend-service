from apps.recordmanagement.models import RecordTemplate, RecordStandardField, \
    RecordEncryptedStandardField, OriginCountry, RecordUsersField, RecordStateField, RecordSelectField
from django.db import transaction


def create_default_record_template(rlc):
    with transaction.atomic():
        template = RecordTemplate.objects.create(name='Default Record Template', rlc=rlc)
        RecordStandardField.objects.create(template=template, order=10, name='Token')
        RecordStandardField.objects.create(template=template, order=20, name='First contact date', field_type='DATE')
        RecordStandardField.objects.create(template=template, order=30, name='Last contact date',
                                           field_type='DATETIME-LOCAL')
        RecordStandardField.objects.create(template=template, order=40, name='First consultation',
                                           field_type='DATETIME-LOCAL')
        RecordStandardField.objects.create(template=template, order=50, name='Official Note')
        RecordUsersField.objects.create(template=template, order=60, name='Consultants')
        options = list(rlc.tags.values_list('name', flat=True))
        if not options:
            options = []
        RecordSelectField.objects.create(template=template, order=70, name='Tags', options=options, multiple=True)
        options = ['Open', 'Closed', 'Waiting', 'Working']
        RecordStateField.objects.create(template=template, order=80, name='State', states=options)
        RecordEncryptedStandardField.objects.create(template=template, order=90, name='Note', field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=100, name='Consultant Team')
        RecordEncryptedStandardField.objects.create(template=template, order=110, name='Lawyer')
        RecordEncryptedStandardField.objects.create(template=template, order=120, name='Related Persons')
        RecordEncryptedStandardField.objects.create(template=template, order=130, name='Contact')
        RecordEncryptedStandardField.objects.create(template=template, order=140, name='BAMF Token')
        RecordEncryptedStandardField.objects.create(template=template, order=145, name='Circumstances')
        RecordEncryptedStandardField.objects.create(template=template, order=150, name='First Correspondence',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=160, name='Next Steps',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=170, name='Status described',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=180, name='Additional facts',
                                                    field_type='TEXTAREA')
        RecordEncryptedStandardField.objects.create(template=template, order=190, name='Client name')
        RecordStandardField.objects.create(template=template, order=200, name='Birthday', field_type='DATE')
        options = list(OriginCountry.objects.values_list('name', flat=True))
        if not options:
            options = []
        RecordSelectField.objects.create(template=template, order=210, name='Origin Country', options=options,
                                         multiple=False)
        RecordEncryptedStandardField.objects.create(template=template, order=220, name='Phone')
        RecordEncryptedStandardField.objects.create(template=template, order=230, name='Client Note')
