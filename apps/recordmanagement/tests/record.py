from django.conf import settings

from apps.recordmanagement.models import RecordTemplate, RecordTextField, Record, RecordEncryptionNew, RecordTextEntry
from apps.recordmanagement.views import RecordTemplateViewSet, RecordTextFieldViewSet, RecordViewSet, \
    RecordTextEntryViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.api.models import Rlc, UserProfile, RlcUser
from django.test import TestCase


###
# General
###
from apps.static.encryption import AESEncryption


class RecordViewSetsWorking(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.rlc = Rlc.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(email='dummy@rlcm.de', name='Dummy 1', rlc=self.rlc)
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(user=self.user, email_confirmed=True, accepted=True)


###
# RecordTemplate
###
class RecordTemplateViewSetWorking(RecordViewSetsWorking):
    def setup_record_template(self):
        view = RecordTemplateViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'RecordTemplate 121',
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.record_template = RecordTemplate.objects.get(name='RecordTemplate 121')
        return response

    def test_record_template_create(self):
        response = self.setup_record_template()
        self.assertEqual(response.status_code, 201)
        self.assertGreater(RecordTemplate.objects.count(), 0)

    def test_record_template_delete(self):
        self.setup_record_template()
        view = RecordTemplateViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordTemplate.objects.count(), 0)

    def test_record_template_update(self):
        self.setup_record_template()
        view = RecordTemplateViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'RecordTemplate 145'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordTemplate.objects.filter(name='RecordTemplate 145').count(), 1)


###
# Fields
###
class RecordTextFieldViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

    def setup_text_field(self):
        self.text_field = RecordTextField.objects.create(name='TextField 234', field_type='TEXT',
                                                         template=self.template)

    def test_text_field_create(self):
        view = RecordTextFieldViewSet.as_view(actions={'post': 'create'})
        data = {
            'name': 'TextField 234',
            'field_type': 'TEXT',
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordTextField.objects.count(), 1)

    def test_text_field_delete(self):
        self.setup_text_field()
        view = RecordTextFieldViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RecordTextField.objects.count(), 0)

    def test_text_field_update(self):
        self.setup_text_field()
        view = RecordTextFieldViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'name': 'TextField 235'
        }
        request = self.factory.patch('', data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RecordTextField.objects.filter(name='TextField 235').count(), 1)


###
# Record
###
class RecordViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')

    def setup_record(self):
        self.record = Record.objects.create(template=self.template)

    def test_record_create(self):
        view = RecordViewSet.as_view(actions={'post': 'create'})
        data = {
            'template': self.template.pk,
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Record.objects.count(), 1)
        self.assertTrue(RecordEncryptionNew.objects.count(), 1)

    def test_record_delete(self):
        self.setup_record()
        view = RecordViewSet.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Record.objects.count(), 0)


###
# RecordTextEntry
###
class RecordTextEntryViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')
        self.field = RecordTextField.objects.create(template=self.template)
        self.record = Record.objects.create(template=self.template)
        aes_key = AESEncryption.generate_secure_key()
        public_key_user = self.user.get_public_key()
        encryption = RecordEncryptionNew(record=self.record, user=self.user, key=aes_key)
        encryption.encrypt(public_key_user=public_key_user)
        encryption.save()

    def setup_entry(self):
        self.entry = RecordTextEntry.objects.create(record=self.record, field=self.field, text=b'')

    def test_entry_create(self):
        view = RecordTextEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'text': 'Hallo',
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordTextEntry.objects.count(), 1)
        entry = RecordTextEntry.objects.first()
        self.assertNotEqual(entry.text, 'Hallo')
        private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        entry.decrypt(user=self.user, private_key_user=private_key_user)
        self.assertEqual(entry.text, 'Hallo')

    def test_entry_update(self):
        self.setup_entry()
        view = RecordTextEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'text': 'Hallo 2'
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        entry = RecordTextEntry.objects.first()
        self.assertNotEqual(entry.text, 'Hallo 2')
        private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        entry.decrypt(user=self.user, private_key_user=private_key_user)
        self.assertEqual(entry.text, 'Hallo 2')
