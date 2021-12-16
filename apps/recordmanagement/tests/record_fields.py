from apps.recordmanagement.models import RecordTemplate, RecordTextField, RecordMetaField, RecordFileField, \
    RecordSelectField, RecordUsersField, RecordStateField
from apps.recordmanagement.views import RecordTextFieldViewSet, RecordMetaFieldViewSet, RecordFileFieldViewSet, \
    RecordSelectFieldViewSet, RecordUsersFieldViewSet, RecordStateFieldViewSet
from apps.recordmanagement.tests import RecordViewSetsWorking
from rest_framework.test import force_authenticate
import json


###
# Fields
###
class RecordFieldViewSetWorking(RecordViewSetsWorking):
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


class RecordTextFieldViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

    def setup_field(self):
        self.text_field = RecordTextField.objects.create(name='TextField 234', field_type='TEXT',
                                                         template=self.template)

    def test_text_field_create(self):
        view = RecordTextFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'field_type': 'TEXT',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordTextField.objects.count(), 1)

    def test_text_field_delete(self):
        self.setup_field()
        view = RecordTextFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordTextField.objects.count(), 0)

    def test_text_field_update(self):
        self.setup_field()
        view = RecordTextFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordTextField.objects.filter(name='Field 235').count(), 1)


class RecordMetaFieldViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

    def setup_field(self):
        self.field = RecordMetaField.objects.create(name='TextField 234', template=self.template)

    def test_field_create(self):
        view = RecordMetaFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordMetaField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordMetaFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordMetaField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordMetaFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordMetaField.objects.filter(name='Field 235').count(), 1)


class RecordUsersFieldViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

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


class RecordFileFieldViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

    def setup_field(self):
        self.field = RecordFileField.objects.create(name='Field 234', template=self.template)

    def test_field_create(self):
        view = RecordFileFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordFileField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordFileFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordFileField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordFileFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordFileField.objects.filter(name='Field 235').count(), 1)


class RecordSelectFieldViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

    def setup_field(self):
        self.field = RecordSelectField.objects.create(name='Field 234', template=self.template,
                                                      options=['Option 1', 'Option 3'])

    def test_field_create(self):
        view = RecordSelectFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'Field 234',
            'template': self.template.pk,
            'options': json.dumps(['Option 1', 'Option 2'])
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordSelectField.objects.count(), 1)

    def test_field_delete(self):
        self.setup_field()
        view = RecordSelectFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordSelectField.objects.count(), 0)

    def test_field_update(self):
        self.setup_field()
        view = RecordSelectFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'Field 235',
            'options': json.dumps(['Option 3', 'Option 4'])
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordSelectField.objects.filter(name='Field 235').count(), 1)
        self.assertEqual(RecordSelectField.objects.last().options, ['Option 3', 'Option 4'])


class RecordStateFieldViewSetWorking(RecordFieldViewSetWorking):
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
