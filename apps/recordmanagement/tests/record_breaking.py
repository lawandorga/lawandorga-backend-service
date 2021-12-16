from apps.recordmanagement.tests.record_entries import RecordEntryViewSetWorkingBase
from apps.recordmanagement.tests.record import RecordViewSetWorking
from apps.recordmanagement.models import RecordEncryptedSelectField, RecordEncryptedSelectEntry, RecordStateField, RecordStateEntry, \
    RecordSelectField, RecordSelectEntry
from apps.recordmanagement.views import RecordEncryptedSelectEntryViewSet, RecordStateFieldViewSet, RecordStateEntryViewSet, \
    RecordSelectEntryViewSet
from rest_framework.test import force_authenticate
import json


###
# Fields
###
class RecordStateFieldViewSetErrors(RecordViewSetWorking):
    def setup_field(self):
        self.field = RecordStateField.objects.create(template=self.template, states=['Closed', 'Option 2'])

    def test_field_can_not_be_created_without_closed(self):
        view = RecordStateFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field',
            'template': self.template.pk,
            'states': json.dumps(['Option 1', 'Option 2'])
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, 'states', status_code=400)

    def test_field_can_not_be_updated_without_closed(self):
        self.setup_field()
        view = RecordStateFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field',
            'template': self.template.pk,
            'states': json.dumps(['Option 1', 'Option 2'])
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertContains(response, 'states', status_code=400)


###
# Entries
###
class RecordeStateEntryViewSetErrors(RecordEntryViewSetWorkingBase):
    def setUp(self):
        super().setUp()
        self.field = RecordStateField.objects.create(template=self.template, states=['Closed', 'Option 1'])

    def setup_entry(self):
        self.entry = RecordStateEntry.objects.create(record=self.record, field=self.field, state='Option 1')

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordStateEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'state': json.dumps(['Option 3']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertContains(response, 'state', status_code=400)


class RecordeSelectEntryViewSetErrors(RecordEntryViewSetWorkingBase):
    def setUp(self):
        super().setUp()
        self.field = RecordSelectField.objects.create(template=self.template, options=['Option 2', 'Option 1'])

    def setup_entry(self):
        self.entry = RecordSelectEntry.objects.create(record=self.record, field=self.field, value=['Option 1'])

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 3']),
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

    def test_values_must_be_in_options(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 2', 'Option 3']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)

    def test_multiple_values_can_be_selected(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 1', 'Option 2']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)


class RecordEncryptedSelectEntryViewSetErrors(RecordEntryViewSetWorkingBase):
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
            'value': json.dumps(['Option 3']),
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

    def test_multiple_values_must_be_in_options(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 2', 'Option 3']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)

    def test_multiple_values_can_be_selected(self):
        self.field.multiple = True
        self.field.save()
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 1', 'Option 2']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
