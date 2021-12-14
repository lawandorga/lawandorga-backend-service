from apps.recordmanagement.models import RecordTemplate, RecordMetaField, RecordSelectField, RecordTextField, \
    OriginCountry


def create_default_record_template(rlc):
    template = RecordTemplate.objects.create(name='Default Record Template')
    RecordMetaField.objects.create(order=10, name='Token')
    RecordMetaField.objects.create(order=20, name='First contact date', type='DATE')
    RecordMetaField.objects.create(order=20, name='Last contact date', type='DATETIME-LOCAL')
    RecordMetaField.objects.create(order=20, name='First consultation', type='DATETIME-LOCAL')
    RecordMetaField.objects.create(order=50)
    # todo: user related field 60
    options = rlc.tags.values_list('name', flat=True)
    RecordSelectField.objects.create(order=70, name='Tags', multiple=True, options=options)
    # todo: state field 80
    RecordTextField.objects.create(order=90, name='Note')
    RecordTextField.objects.create(order=100, name='Consultant Team')
    RecordTextField.objects.create(order=110, name='Lawyer')
    RecordTextField.objects.create(order=120, name='Related Persons')
    RecordTextField.objects.create(order=130, name='Contact')
    RecordTextField.objects.create(order=140, name='BAMF Token')
    RecordTextField.objects.create(order=150, name='First Correspondence')
    RecordTextField.objects.create(order=160, name='Next Steps')
    RecordTextField.objects.create(order=170, name='Status described')
    RecordTextField.objects.create(order=180, name='Additional facts')
    RecordTextField.objects.create(order=190, name='Client name')
    # todo: date field 200
    options = OriginCountry.objects.values_list('name', flat=True)
    RecordSelectField.objects.create(210, name='Origin County', options=options)
    RecordTextField.objects.create(order=220, name='Phone')
    RecordTextField.objects.create(order=230, name='Client Note')


