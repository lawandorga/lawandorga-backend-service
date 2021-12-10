from apps.recordmanagement.models import RecordSelectField, RecordSelectEntry
from apps.recordmanagement.tests import RecordEntryViewSetWorking
from apps.recordmanagement.views import RecordSelectEntryViewSet
from rest_framework.test import force_authenticate
import json


class RecordSelectEntryViewSetErrors(RecordEntryViewSetWorking):
    def setUp(self):
        super().setUp()
        self.field = RecordSelectField.objects.create(template=self.template, options=['Option 1', 'Option 2'])

    def setup_entry(self):
        entry = RecordSelectEntry(record=self.record, field=self.field, value=json.dumps(['Option 1']))
        entry.encrypt(aes_key_record=self.aes_key_record)
        entry.save()
        self.entry = RecordSelectEntry.objects.first()

    def test_value_must_be_in_options(self):
        self.setup_entry()
        view = RecordSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 3']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 400)

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

    def test_multiple_values_must_be_in_options(self):
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
