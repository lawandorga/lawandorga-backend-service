from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.files.models import File
from apps.recordmanagement.models import RecordTemplate, RecordEncryptedStandardField, Record, RecordEncryptionNew, \
    RecordEncryptedStandardEntry, RecordStandardField, RecordStandardEntry, RecordEncryptedFileField, \
    RecordEncryptedFileEntry, \
    RecordUsersField, RecordUsersEntry, RecordStateField, RecordStateEntry, RecordSelectField, RecordSelectEntry, \
    RecordEncryptedSelectEntry, RecordEncryptedSelectField, RecordMultipleEntry, RecordMultipleField
from apps.recordmanagement.tests import BaseRecord
from apps.recordmanagement.views import RecordEncryptedStandardEntryViewSet, RecordStandardEntryViewSet, \
    RecordEncryptedFileEntryViewSet, \
    RecordUsersEntryViewSet, RecordStateEntryViewSet, RecordSelectEntryViewSet, RecordEncryptedSelectEntryViewSet, \
    RecordMultipleEntryViewSet
from apps.static.encryption import AESEncryption
from rest_framework.test import force_authenticate
from apps.api.models import UserProfile
from django.conf import settings
from django.test import TestCase
import json
import sys
import io


###
# Base
###
class BaseRecordEntry(BaseRecord):
    def setUp(self):
        super().setUp()
        self.template = RecordTemplate.objects.create(rlc=self.rlc, name='Record Template')
        self.record = Record.objects.create(template=self.template)
        self.aes_key_record = AESEncryption.generate_secure_key()
        public_key_user = self.user.get_public_key()
        encryption = RecordEncryptionNew(record=self.record, user=self.user, key=self.aes_key_record)
        encryption.encrypt(public_key_user=public_key_user)
        encryption.save()


class GenericRecordEntry(BaseRecordEntry):
    view = None

    def setUp(self):
        super().setUp()
        self.entry = None

    def setup_entry(self):
        raise NotImplementedError('Needs to be implemented.')

    def test_entry_delete(self):
        self.setup_entry()
        view = self.view.as_view(actions={'delete': 'destroy'})
        request = self.factory.delete('')
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 204)


###
# Entries
###
class RecordFileEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordEncryptedFileEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedFileField.objects.create(template=self.template)
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    def setup_entry(self):
        self.entry = RecordEncryptedFileEntry.objects.create(record=self.record, field=self.field, file=self.get_file())

    def get_file(self, text='test string'):
        file = io.BytesIO(bytes(text, 'utf-8'))
        file = InMemoryUploadedFile(file, 'FileField', 'test.txt', 'text/plain', sys.getsizeof(file), None)
        return file

    def test_entry_create(self):
        view = RecordEncryptedFileEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'file': self.get_file('test-string')
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        respone = view(request)
        self.assertEqual(respone.status_code, 201)
        self.assertTrue(RecordEncryptedFileEntry.objects.count(), 1)
        entry = RecordEncryptedFileEntry.objects.first()
        self.assertNotEqual(entry.file.read(), 'test-string')
        entry.file.seek(0)
        file = entry.decrypt_file(aes_key_record=self.aes_key_record)
        self.assertEqual(b'test-string', file.read())
        # clean up the after the tests
        entry.delete()

    def test_entry_update(self):
        self.setup_entry()
        view = RecordEncryptedFileEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'file': self.get_file('new text')
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        entry = RecordEncryptedFileEntry.objects.first()
        self.assertNotEqual(entry.file.read(), 'new text')
        entry.file.seek(0)
        file = entry.decrypt_file(aes_key_record=self.aes_key_record)
        self.assertEqual(b'new text', file.read())
        # clean up after the tests
        entry.delete()


class RecordStandardEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordStandardEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordStandardField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordStandardEntry.objects.create(record=self.record, field=self.field, value='test text')

    def test_entry_create(self):
        view = RecordStandardEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': 'Hallo'
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        respone = view(request)
        self.assertEqual(respone.status_code, 201)
        self.assertTrue(RecordStandardEntry.objects.count(), 1)
        self.assertEqual(RecordStandardEntry.objects.first().value, 'Hallo')

    def test_entry_update(self):
        self.setup_entry()
        view = RecordStandardEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Hallo 2'
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        entry = RecordStandardEntry.objects.first()
        self.assertEqual(entry.value, 'Hallo 2')


class RecordUsersEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordUsersEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordUsersField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordUsersEntry.objects.create(record=self.record, field=self.field)
        self.entry.value.set(UserProfile.objects.all())

    def test_entry_create(self):
        view = RecordUsersEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': [u.pk for u in UserProfile.objects.all()]
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordUsersEntry.objects.count(), 1)
        self.assertEqual(
            list(RecordUsersEntry.objects.first().value.values_list('pk', flat=True)),
            list(UserProfile.objects.all().values_list('pk', flat=True))
        )

    def test_entry_update(self):
        self.setup_entry()
        view = RecordUsersEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': []
        }
        request = self.factory.patch('', data=data, format='json')
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        entry = RecordUsersEntry.objects.first()
        self.assertEqual(entry.value.all().count(), UserProfile.objects.none().count())


class RecordEncryptedStandardEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordEncryptedStandardEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedStandardField.objects.create(template=self.template)

    def setup_entry(self):
        self.entry = RecordEncryptedStandardEntry.objects.create(record=self.record, field=self.field, value=b'')

    def test_entry_create(self):
        view = RecordEncryptedStandardEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': 'Hallo',
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordEncryptedStandardEntry.objects.count(), 1)
        entry = RecordEncryptedStandardEntry.objects.first()
        self.assertNotEqual(entry.value, 'Hallo')
        private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        entry.decrypt(user=self.user, private_key_user=private_key_user)
        self.assertEqual(entry.value, 'Hallo')

    def test_entry_update(self):
        self.setup_entry()
        view = RecordEncryptedStandardEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Hallo 2'
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        entry = RecordEncryptedStandardEntry.objects.first()
        self.assertNotEqual(entry.value, 'Hallo 2')
        private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        entry.decrypt(user=self.user, private_key_user=private_key_user)
        self.assertEqual(entry.value, 'Hallo 2')


class RecordStateEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordStateEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordStateField.objects.create(template=self.template, options=['Closed', 'Option 2'])

    def setup_entry(self):
        self.entry = RecordStateEntry.objects.create(record=self.record, field=self.field, value='Option 1')

    def test_entry_create(self):
        view = RecordStateEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': 'Option 2',
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordStateEntry.objects.count(), 1)
        entry = RecordStateEntry.objects.first()
        self.assertEqual(entry.value, "Option 2")

    def test_entry_update(self):
        self.setup_entry()
        view = RecordStateEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Closed',
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(RecordStateEntry.objects.count(), 1)
        entry = RecordStateEntry.objects.first()
        self.assertEqual(entry.value, "Closed")


class RecordSelectEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordSelectEntryViewSet
    model = RecordSelectEntry
    field = RecordSelectField

    def setUp(self):
        super().setUp()
        self.field = self.field.objects.create(template=self.template, options=['Option 1', 'Option 2'])

    def setup_entry(self):
        self.entry = self.model.objects.create(record=self.record, field=self.field, value=['Option 1', 'Option 2'])

    def test_entry_create(self):
        view = self.view.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': 'Option 1',
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.model.objects.count(), 1)
        entry = self.model.objects.first()
        self.assertEqual(entry.value, "Option 1")

    def test_entry_update(self):
        self.setup_entry()
        view = self.view.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Option 2',
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.count(), 1)
        entry = self.model.objects.first()
        self.assertEqual(entry.value, "Option 2")


class RecordMultipleEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordMultipleEntryViewSet
    model = RecordMultipleEntry
    field = RecordMultipleField

    def setUp(self):
        super().setUp()
        self.field = self.field.objects.create(template=self.template, options=['Option 1', 'Option 2'])

    def setup_entry(self):
        self.entry = self.model.objects.create(record=self.record, field=self.field, value=['Option 1', 'Option 2'])

    def test_entry_create(self):
        view = self.view.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': json.dumps(['Option 1']),
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.model.objects.count(), 1)
        entry = self.model.objects.first()
        self.assertEqual(entry.value, ["Option 1"])

    def test_entry_update(self):
        self.setup_entry()
        view = self.view.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': json.dumps(['Option 2']),
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.model.objects.count(), 1)
        entry = self.model.objects.first()
        self.assertEqual(entry.value, ["Option 2"])


class RecordEncryptedSelectEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordEncryptedSelectEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedSelectField.objects.create(template=self.template, options=['Option 1', 'Option 2'])

    def setup_entry(self):
        entry = RecordEncryptedSelectEntry(record=self.record, field=self.field, value='Option 1')
        entry.encrypt(aes_key_record=self.aes_key_record)
        entry.save()
        self.entry = RecordEncryptedSelectEntry.objects.first()

    def test_entry_create(self):
        view = RecordEncryptedSelectEntryViewSet.as_view(actions={'post': 'create'})
        data = {
            'record': self.record.pk,
            'field': self.field.pk,
            'value': 'Option 1',
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(RecordEncryptedSelectEntry.objects.count(), 1)
        entry = RecordEncryptedSelectEntry.objects.first()
        self.assertNotEqual(entry.value, "Option 1")
        private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        entry.decrypt(user=self.user, private_key_user=private_key_user)
        self.assertEqual(entry.value, "Option 1")

    def test_entry_update(self):
        self.setup_entry()
        view = RecordEncryptedSelectEntryViewSet.as_view(actions={'patch': 'partial_update'})
        data = {
            'value': 'Option 2',
        }
        request = self.factory.patch('', data=data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(RecordEncryptedSelectEntry.objects.count(), 1)
        entry = RecordEncryptedSelectEntry.objects.first()
        self.assertNotEqual(entry.value, "Option 2")
        private_key_user = self.user.get_private_key(password_user=settings.DUMMY_USER_PASSWORD)
        entry.decrypt(user=self.user, private_key_user=private_key_user)
        self.assertEqual(entry.value, "Option 2")


class RecordEncryptedFileEntryViewSetWorking(GenericRecordEntry, TestCase):
    view = RecordEncryptedFileEntryViewSet

    def setUp(self):
        super().setUp()
        self.field = RecordEncryptedFileField.objects.create(template=self.template)
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    def setup_entry(self):
        entry = RecordEncryptedFileEntry(record=self.record, field=self.field)
        file = io.BytesIO(b'test string')
        file = InMemoryUploadedFile(file, 'FileField', 'test.txt', 'text/plain', sys.getsizeof(file), None)
        entry.file = RecordEncryptedFileEntry.encrypt_file(file, self.record, aes_key_record=self.aes_key_record)
        entry.save()
        self.entry = RecordEncryptedFileEntry.objects.first()

    def test_upload(self):
        view = self.view.as_view(actions={'post': 'create'})
        file = io.BytesIO(b'test string')
        file = InMemoryUploadedFile(file, 'FileField', 'test.txt', 'text/plain', sys.getsizeof(file), None)
        data = {
            'record': self.record.id,
            'field': self.field.id,
            'file': file
        }
        request = self.factory.post('', data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, 'test.txt', status_code=201)
        entry = RecordEncryptedFileEntry.objects.first()
        self.assertFalse(b'test string' in entry.file.read())
        entry.file.delete()  # clean up

    def test_download(self):
        self.setup_entry()
        view = self.view.as_view(actions={'get': 'download'})
        request = self.factory.get('')
        force_authenticate(request, self.user)
        response = view(request, pk=self.entry.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'test string' in b''.join(response.streaming_content))
