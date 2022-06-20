from django.conf import settings
from django.core.files.storage import default_storage
from django.test import TestCase
from rest_framework.test import force_authenticate

from apps.files.models import File
from apps.files.tests.file import FileTestsBase
from apps.files.views import FileViewSet

settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


class FileTestsBreaking(FileTestsBase, TestCase):
    def test_retrieve_file_not_on_server(self):
        # setup and delete the file for this test case to be like reality
        self.setup_file()
        default_storage.delete(self.file.file.name)
        # test case
        view = FileViewSet.as_view(actions={"get": "retrieve"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request, pk=self.file.pk)
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
        view = FileViewSet.as_view(actions={"get": "retrieve"})
        request = self.factory.get("")
        force_authenticate(request, self.user)
        response = view(request, pk=self.file.pk)
        self.assertContains(response, "The file could not be found", status_code=404)
        file = File.objects.get(pk=self.file.pk)
        self.assertEqual(file.exists, False)
        # clean up
        file.file.delete()

    def test_file_with_same_name_does_not_overwrite_another(self):
        view = FileViewSet.as_view(actions={"post": "create"})
        data = {
            "file": self.get_file("1"),
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        file1 = File.objects.get(pk=response.data["id"])
        file1.file.seek(0)
        f = file1.decrypt_file(aes_key_rlc=self.aes_key_rlc)
        self.assertEqual(f.read(), b"1")
        # upload the same file and check for the content of the first to still be 1
        data = {
            "file": self.get_file("2"),
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        file2 = File.objects.get(pk=response.data["id"])
        self.assertEqual(response.status_code, 201)
        file1 = File.objects.get(pk=file1.pk)
        f = file1.decrypt_file(aes_key_rlc=self.aes_key_rlc)
        self.assertEqual(f.read(), b"1")
        # clean up
        file1.file.delete()
        file2.file.delete()
