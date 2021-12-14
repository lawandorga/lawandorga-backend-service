from apps.recordmanagement.models import RecordTemplate, RecordMetaField, RecordSelectField, RecordTextField, \
    OriginCountry, RecordUsersField


def create_default_record_template(rlc):
    template = RecordTemplate.objects.create(name='Default Record Template')
    RecordMetaField.objects.create(template=template, order=10, name='Token')
    RecordMetaField.objects.create(template=template, order=20, name='First contact date', type='DATE')
    RecordMetaField.objects.create(template=template, order=20, name='Last contact date', type='DATETIME-LOCAL')
    RecordMetaField.objects.create(template=template, order=20, name='First consultation', type='DATETIME-LOCAL')
    RecordMetaField.objects.create(template=template, order=50, name='Official Note')
    RecordUsersField.objects.create(template=template, order=60, name='Consultants')
    options = rlc.tags.values_list('name', flat=True)
    RecordSelectField.objects.create(template=template, order=70, name='Tags', multiple=True, options=options)
    # todo: state field 80
    options = ['Open', 'Closed', 'Waiting', 'Working']
    RecordTextField.objects.create(template=template, order=90, name='Note')
    RecordTextField.objects.create(template=template, order=100, name='Consultant Team')
    RecordTextField.objects.create(template=template, order=110, name='Lawyer')
    RecordTextField.objects.create(template=template, order=120, name='Related Persons')
    RecordTextField.objects.create(template=template, order=130, name='Contact')
    RecordTextField.objects.create(template=template, order=140, name='BAMF Token')
    RecordTextField.objects.create(template=template, order=150, name='First Correspondence')
    RecordTextField.objects.create(template=template, order=160, name='Next Steps')
    RecordTextField.objects.create(template=template, order=170, name='Status described')
    RecordTextField.objects.create(template=template, order=180, name='Additional facts')
    RecordTextField.objects.create(template=template, order=190, name='Client name')
    RecordTextField.objects.create(template=template, order=200, name='Birthday', type='DATE')
    options = OriginCountry.objects.values_list('name', flat=True)
    RecordSelectField.objects.create(template=template, order=210, name='Origin County', options=options)
    RecordTextField.objects.create(template=template, order=220, name='Phone')
    RecordTextField.objects.create(template=template, order=230, name='Client Note')
