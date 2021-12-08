from django.core.files.uploadedfile import InMemoryUploadedFile
from apps.static.encryption import AESEncryption
from apps.files.models import File, Folder
from apps.api.models import Rlc
from django.conf import settings
from django.test import TestCase
import sys
import io


settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'


class FileTests(TestCase):
    def setUp(self):
        self.rlc = Rlc.objects.create(name='Test RLC')
        self.folder = Folder.objects.create(name='files', rlc=self.rlc)

    def test_upload_and_delete_file(self):
        file = File.objects.create(name='test-file.txt', folder=self.folder)
        file.key = 'tests/test-file.txt'
        file.save()
        key = AESEncryption.generate_secure_key()
        txt_file = io.BytesIO(b'test string')
        txt_file = InMemoryUploadedFile(txt_file, 'FileField', 'test.txt', 'text/plain', sys.getsizeof(txt_file), None)
        file.upload(txt_file, key)
        self.assertTrue(file.exists_on_s3())
        file.delete_on_cloud()
        self.assertFalse(file.exists_on_s3())
