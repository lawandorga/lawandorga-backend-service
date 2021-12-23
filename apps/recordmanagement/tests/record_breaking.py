from apps.recordmanagement.tests.record_entries import BaseRecordEntry
from apps.recordmanagement.tests.record import BaseRecord
from apps.recordmanagement.models import RecordEncryptedSelectField, RecordEncryptedSelectEntry, RecordStateField, \
    RecordStateEntry, \
    RecordSelectField, RecordSelectEntry, RecordEncryptedStandardField, RecordEncryptedStandardEntry, \
    RecordMultipleEntry, RecordMultipleField
from apps.recordmanagement.views import RecordEncryptedSelectEntryViewSet, RecordStateFieldViewSet, \
    RecordStateEntryViewSet, \
    RecordSelectEntryViewSet, RecordEncryptedStandardEntryViewSet, RecordMultipleEntryViewSet
from rest_framework.test import force_authenticate
from django.test import TestCase
import json


###
# Fields
###
class RecordStateFieldViewSetErrors(BaseRecord, TestCase):
    def setup_field(self):
        self.field = RecordStateField.objects.create(template=self.template, options=['Closed', 'Option 2'])

    def test_field_can_not_be_created_without_closed(self):
        view = RecordStateFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field',
            'template': self.template.pk,
            'options': json.dumps(['Option 1', 'Option 2'])
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, 'options', status_code=400)

    def test_field_can_not_be_updated_without_closed(self):
        self.setup_field()
        view = RecordStateFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field',
            'template': self.template.pk,
            'options': json.dumps(['Option 1', 'Option 2'])
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertContains(response, 'options', status_code=400)


###
# Entries
###
class RecordStateEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        RecordStateField.objects.all().delete()
        self.field = RecordStateField.objects.create(template=self.template, options=['Closed', 'Option 1'])

    def setup_entry(self):
        self.entry = RecordStateEntry.objects.create(record=self.record, field=self.field, value='Option 1')

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordStateEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 3']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertContains(response, 'state', status_code=400)


class RecordEncryptedStandardEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedStandardField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordEncryptedStandardEntry(record=self.record, field=self.field, value='Test Text')
        self.entry.encrypt(aes_key_record=self.aes_key_record)
        self.entry.save()
        self.entry.decrypt(aes_key_record=self.aes_key_record)

    def test_weird_values_work_on_update(self):
        self.setup_entry()
        view = RecordEncryptedStandardEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'url': 'whatever should be ignored',
            'value': json.dumps({"isTrusted": True}),
        }
        request = self.factory.patch('', data=data, format='json')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        entry = RecordEncryptedStandardEntry.objects.first()
        entry.decrypt(aes_key_record=self.aes_key_record)
        self.assertEqual(entry.value, json.dumps({"isTrusted": True}))


class RecordeSelectEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordSelectField.objects.create(template=self.template, options=['Option 2', 'Option 1'])

    def setup_entry(self):
        self.entry = RecordSelectEntry.objects.create(record=self.record, field=self.field, value=['Option 1'])

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Option 3',
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertContains(response, 'value', status_code=400)

    def test_only_one_value_can_be_selected(self):
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 1', 'Option 2']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)


class RecordMultipleEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordMultipleField.objects.create(template=self.template, options=['Option 2', 'Option 1'])

    def setup_entry(self):
        self.entry = RecordMultipleEntry.objects.create(record=self.record, field=self.field, value=['Option 1'])

    def test_multiple_values_can_be_selected(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordMultipleEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 1', 'Option 2']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)

    def test_values_must_be_in_options(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordMultipleEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 2', 'Option 3']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)


class RecordEncryptedSelectEntryViewSetErrors(BaseRecordEntry, TestCase):
    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedSelectField.objects.create(template=self.template, options=['Option 1', 'Option 2'])

    def setup_entry(self):
        entry = RecordEncryptedSelectEntry(record=self.record, field=self.field, value=json.dumps(['Option 1']))
        entry.encrypt(aes_key_record=self.aes_key_record)
        entry.save()
        self.entry = RecordEncryptedSelectEntry.objects.first()

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Option 3',
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)

    def test_only_one_value_can_be_selected(self):
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 1', 'Option 2']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)
