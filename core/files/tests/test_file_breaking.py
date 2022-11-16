from django.conf import settings
from django.core.files.storage import default_storage
from django.test import Client, TestCase

from core.models import File

from .test_file import FileTestsBase

settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


class FileTestsBreaking(FileTestsBase, TestCase):
    def test_retrieve_file_not_on_server(self):
        # setup and delete the file for this test case to be like reality
        self.setup_file()
        default_storage.delete(self.file.file.name)
        # test case
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.get("/api/files/file_base/{}/".format(self.file.pk))
        self.assertContains(response, "The file could not be found", status_code=404)
        file = File.objects.get(pk=self.file.pk)
        self.assertEqual(file.exists, False)
        # clean up
        file.file.delete()

    def test_retrieve_file_with_no_name(self):
        # setup and unset file name to equal reality
        self.setup_file()
        self.file.file.delete()
        self.file.file.name = ""
        self.file.save()
        # test case
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.get("/api/files/file_base/{}/".format(self.file.pk))
        self.assertContains(response, "The file could not be found", status_code=404)
        file = File.objects.get(pk=self.file.pk)
        self.assertEqual(file.exists, False)
        # clean up
        file.file.delete()

    def test_file_with_same_name_does_not_overwrite_another(self):
        data = {
            "file": self.get_file("1"),
        }
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.post("/api/files/file_base/", data)
        self.assertEqual(response.status_code, 201)
        file1 = File.objects.get(pk=response.json()["id"])
        file1.file.seek(0)
        f = file1.decrypt_file(aes_key_rlc=self.aes_key_rlc)
        self.assertEqual(f.read(), b"1")
        # upload the same file and check for the content of the first to still be 1
        data = {
            "file": self.get_file("2"),
        }
        c = Client()
        c.login(email=self.user.email, password=settings.DUMMY_USER_PASSWORD)
        response = c.post("/api/files/file_base/", data)
        file2 = File.objects.get(pk=response.json()["id"])
        self.assertEqual(response.status_code, 201)
        file1 = File.objects.get(pk=file1.pk)
        f = file1.decrypt_file(aes_key_rlc=self.aes_key_rlc)
        self.assertEqual(f.read(), b"1")
        # clean up
        file1.file.delete()
        file2.file.delete()
