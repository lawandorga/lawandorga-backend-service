from apps.recordmanagement.models import RecordTemplate, RecordEncryptedStandardField, RecordStandardField, RecordEncryptedFileField, \
    RecordEncryptedSelectField, RecordUsersField, RecordStateField, RecordSelectField
from apps.recordmanagement.views import RecordEncryptedStandardFieldViewSet, RecordStandardFieldViewSet, RecordEncryptedFileFieldViewSet, \
    RecordEncryptedSelectFieldViewSet, RecordUsersFieldViewSet, RecordStateFieldViewSet, RecordSelectFieldViewSet
from apps.recordmanagement.tests import BaseRecord
from rest_framework.test import force_authenticate
from django.test import TestCase
import json


###
# Base
###
class BaseRecordField(BaseRecord):
    pass


class GenericRecordField(BaseRecordField):
    view = None
    model = None
    # create
    create_data = None
    create_test = None
    # update
    update_data = None
    update_test = None

    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')
        if self.create_data is None:
            self.create_data = self.get_create_data()
        if self.update_data is None:
            self.update_data = self.get_update_data()

    def setup_field(self):
        raise NotImplementedError('This method needs to be implemented.')

    def get_create_data(self):
        raise NotImplementedError('This method needs to be implemented.')

    def get_update_data(self):
        raise NotImplementedError('This method needs to be implemented.')

    def test_create(self):
        view = self.view.as_view(actions={'post': 'create'})
        request = self.factory.post('', self.create_data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.model.objects.count(), 1)
        field = self.model.objects.first()
        for key in self.create_test:
            self.assertEqual(getattr(field, key), self.create_test[key])

    def test_update(self):
        self.setup_field()
        view = self.view.as_view(actions={'patch': 'partial_update'})
        request = self.factory.patch('', self.update_data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.model.objects.count(), 1)
        field = self.model.objects.first()
        for key in self.update_test:
            self.assertEqual(getattr(field, key), self.update_test[key])

    def test_delete(self):
        self.setup_field()
        view = self.view.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.model.objects.count(), 0)


###
# Fields
###
class RecordStandardFieldViewSetWorking(BaseRecordField, TestCase):
    def setup_field(self):
        self.field = RecordStandardField.objects.create(name='TextField 234', template=self.template)

    def test_field_create(self):
        view = RecordStandardFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordStandardField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordStandardFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordStandardField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordStandardFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordStandardField.objects.filter(name='Field 235').count(), 1)


class RecordEncryptedStandardFieldViewSetWorking(BaseRecordField, TestCase):
    def setup_field(self):
        self.text_field = RecordEncryptedStandardField.objects.create(name='TextField 234', field_type='TEXT',
                                                                      template=self.template)

    def test_text_field_create(self):
        view = RecordEncryptedStandardFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'field_type': 'TEXT',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordEncryptedStandardField.objects.count(), 1)

    def test_text_field_delete(self):
        self.setup_field()
        view = RecordEncryptedStandardFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordEncryptedStandardField.objects.count(), 0)

    def test_text_field_update(self):
        self.setup_field()
        view = RecordEncryptedStandardFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordEncryptedStandardField.objects.filter(name='Field 235').count(), 1)


class RecordUsersFieldViewSetWorking(BaseRecordField, TestCase):
    def setup_field(self):
        self.field = RecordUsersField.objects.create(name='Field 234', template=self.template)

    def test_field_create(self):
        view = RecordUsersFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordUsersField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordUsersFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordUsersField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordUsersFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordUsersField.objects.filter(name='Field 235').count(), 1)


class RecordEncryptedFileFieldViewSetWorking(BaseRecordField, TestCase):
    def setup_field(self):
        self.field = RecordEncryptedFileField.objects.create(name='Field 234', template=self.template)

    def test_field_create(self):
        view = RecordEncryptedFileFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordEncryptedFileField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordEncryptedFileFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordEncryptedFileField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordEncryptedFileFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordEncryptedFileField.objects.filter(name='Field 235').count(), 1)


class RecordEncryptedSelectFieldViewSetWorking(BaseRecordField, TestCase):
    def setup_field(self):
        self.field = RecordEncryptedSelectField.objects.create(name='Field 234', template=self.template,
                                                               options=['Option 1', 'Option 3'])

    def test_field_create(self):
        view = RecordEncryptedSelectFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
            'options': json.dumps(['Option 1', 'Option 2'])
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordEncryptedSelectField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordEncryptedSelectFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordEncryptedSelectField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordEncryptedSelectFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235',
            'options': json.dumps(['Option 3', 'Option 4'])
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordEncryptedSelectField.objects.filter(name='Field 235').count(), 1)
        self.assertEqual(RecordEncryptedSelectField.objects.last().options, ['Option 3', 'Option 4'])


class RecordStateFieldViewSetWorking(GenericRecordField, TestCase):
    model = RecordStateField
    view = RecordStateFieldViewSet
    # create
    create_states = ['Closed', 'Option 1', 'Option 2']
    create_test = {
        'states': create_states
    }
    # update
    update_states = ['Closed', 'Option 4']
    update_data = {
        'states': json.dumps(update_states),
    }
    update_test = {
        'states': update_states
    }

    def setup_field(self):
        self.field = RecordStateField.objects.create(template=self.template, states=['Closed', 'Option 4'])

    def get_create_data(self):
        return {
            'name': 'Field 234',
            'template': self.template.pk,
            'states': json.dumps(self.create_states)
        }


class RecordSelectFieldViewSetWorking(GenericRecordField, TestCase):
    model = RecordSelectField
    view = RecordSelectFieldViewSet
    # create
    create_options = ['Option 1', 'Option 2']
    create_test = {
        'options': create_options
    }
    # update
    update_options = ['Closed', 'Option 4']
    update_data = {
        'options': json.dumps(update_options),
    }
    update_test = {
        'options': update_options
    }

    def setup_field(self):
        self.field = RecordSelectField.objects.create(template=self.template, options=['Option 5', 'Option 4'])

    def get_create_data(self):
        return {
            'name': 'Field',
            'template': self.template.pk,
            'options': json.dumps(self.create_options)
        }
