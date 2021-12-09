from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.recordmanagement.models import RecordTemplate, RecordTextField, Record, RecordEncryptionNew, \
    RecordTextEntry, RecordMetaField, RecordMetaEntry, RecordFileField, RecordFileEntry, RecordSelectField, \
    RecordSelectEntry
from apps.recordmanagement.views import RecordTemplateViewSet, RecordTextFieldViewSet, RecordViewSet, \
    RecordTextEntryViewSet, RecordMetaEntryViewSet, RecordFileEntryViewSet, RecordMetaFieldViewSet, \
    RecordFileFieldViewSet, RecordSelectFieldViewSet
from apps.static.encryption import AESEncryption
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.api.models import Rlc, UserProfile, RlcUser
from django.conf import settings
from django.test import TestCase
import json
import sys
import io


###
# General
###
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
# RecordEntry
###
class RecordEntryViewSetWorking(RecordViewSetsWorking):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')
        self.record = Record.objects.create(template=self.template)
        self.aes_key_record = AESEncryption.generate_secure_key()
        public_key_user = self.user.get_public_key()
        encryption = RecordEncryptionNew(record=self.record, user=self.user, key=self.aes_key_record)
        encryption.encrypt(public_key_user=public_key_user)
        encryption.save()


class RecordFileEntryViewSetWorking(RecordEntryViewSetWorking):
    def setUp(self):
        super().setUp()
        self.field = RecordFileField.objects.create(template=self.template)
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    def setup_entry(self):
        self.entry = RecordFileEntry.objects.create(record=self.record, field=self.field, file=self.get_file())

    def get_file(self, text='test string'):
        file = io.BytesIO(bytes(text, 'utf-8'))
        file = InMemoryUploadedFile(file, 'FileField', 'test.txt', 'text/plain', sys.getsizeof(file), None)
        return file

    def test_entry_create(self):
        view = RecordFileEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'file': self.get_file('test-string')
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        respone = view(request)
        self.assertEqual(respone.status_code, 201)
        self.assertTrue(RecordFileEntry.objects.count(), 1)
        entry = RecordFileEntry.objects.first()
        self.assertNotEqual(entry.file.read(), 'test-string')
        entry.file.seek(0)
        file = entry.decrypt_file(aes_key_record=self.aes_key_record)
        self.assertEqual(b'test-string', file.read())
        # clean up the after the tests
        entry.delete()

    def test_entry_update(self):
        self.setup_entry()
        view = RecordFileEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'file': self.get_file('new text')
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        entry = RecordFileEntry.objects.first()
        self.assertNotEqual(entry.file.read(), 'new text')
        entry.file.seek(0)
        file = entry.decrypt_file(aes_key_record=self.aes_key_record)
        self.assertEqual(b'new text', file.read())
        # clean up after the tests
        entry.delete()


class RecordMetaEntryViewSetWorking(RecordEntryViewSetWorking):
    def setUp(self):
        super().setUp()
        self.field = RecordMetaField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordMetaEntry.objects.create(record=self.record, field=self.field, text='test text')

    def test_entry_create(self):
        view = RecordMetaEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'text': 'Hallo'
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        respone = view(request)
        self.assertEqual(respone.status_code, 201)
        self.assertTrue(RecordMetaEntry.objects.count(), 1)
        self.assertEqual(RecordMetaEntry.objects.first().text, 'Hallo')

    def test_entry_update(self):
        self.setup_entry()
        view = RecordMetaEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'text': 'Hallo 2'
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        entry = RecordMetaEntry.objects.first()
        self.assertEqual(entry.text, 'Hallo 2')


class RecordTextEntryViewSetWorking(RecordEntryViewSetWorking):
    def setUp(self):
        super().setUp()
        self.field = RecordTextField.objects.create(template=self.template)

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


class RecordSelectEntryViewSetWorking(RecordEntryViewSetWorking):
    def setUp(self):
        super().setUp()
        self.field = RecordSelectField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordSelectEntry.objects.create(record=self.record, field=self.field,
                                                      options=['Option 1', 'Option 2'])
