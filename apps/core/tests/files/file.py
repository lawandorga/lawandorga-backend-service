import io
import sys

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.core.fixtures import create_folder_permissions, create_permissions
from apps.core.models import (
    File,
    Folder,
    HasPermission,
    Org,
    Permission,
    RlcUser,
    UserProfile,
)
from apps.core.static import PERMISSION_FILES_WRITE_ALL_FOLDERS
from apps.core.views import FileViewSet

settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


class FileTestsBase:
    def setUp(self):
        create_folder_permissions()
        create_permissions()
        self.factory = APIRequestFactory()
        self.rlc = Org.objects.create(name="Test RLC")
        self.user = UserProfile.objects.create(
            email="dummy@law-orga.de", name="Dummy 1", rlc=self.rlc
        )
        self.user.set_password(settings.DUMMY_USER_PASSWORD)
        self.user.save()
        self.rlc_user = RlcUser.objects.create(
            user=self.user, email_confirmed=True, accepted=True
        )
        self.folder = Folder.objects.get(parent=None, rlc=self.rlc)
        self.private_key_user = self.user.get_private_key(
            password_user=settings.DUMMY_USER_PASSWORD
        )
        self.aes_key_rlc = self.user.rlc.get_aes_key(
            user=self.user, private_key_user=self.private_key_user
        )
        HasPermission.objects.create(
            user_has_permission=self.user,
            permission=Permission.objects.get(name=PERMISSION_FILES_WRITE_ALL_FOLDERS),
        )

    def setup_file(self):
        file = File.encrypt_file(self.get_file(), self.aes_key_rlc)
        self.file = File.objects.create(name="test.txt", folder=self.folder, file=file)

    def get_file(self, text="test text inside the file"):
        file = io.BytesIO(bytes(text, "utf-8"))
        file = InMemoryUploadedFile(
            file, "FileField", "test.txt", "text/plain", sys.getsizeof(file), None
        )
        return file


class FileTests(FileTestsBase, TestCase):
    def test_create_file(self):
        view = FileViewSet.as_view(actions={"post": "create"})
        data = {
            "file": self.get_file(),
        }
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "test.txt", status_code=201)
        file = File.objects.get(pk=response.data["id"])
        self.assertEqual("test.txt", file.name)
        self.assertNotEqual(file.file.read(), b"test text inside the file")
        file.file.seek(0)
        f = file.decrypt_file(aes_key_rlc=self.aes_key_rlc)
        self.assertEqual(f.read(), b"test text inside the file")
        # clean up
        file.file.delete()

    def test_update_file(self):
        self.setup_file()
        new_folder = Folder.objects.create(
            name="Test", parent=self.folder, rlc=self.rlc
        )
        view = FileViewSet.as_view(actions={"patch": "partial_update"})
        data = {"name": "Neuer Name.txt", "folder": new_folder.pk}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.file.pk)
        file = File.objects.get(pk=response.data["id"])
        self.assertEqual("Neuer Name.txt", file.name)
        self.assertEqual("Test", file.folder.name)
        # clean up
        file.file.delete()

    def test_delete_file(self):
        self.setup_file()
        view = FileViewSet.as_view(actions={"delete": "destroy"})
        request = self.factory.delete("")
        force_authenticate(request, self.user)
        response = view(request, pk=self.file.pk)
        self.assertEqual(File.objects.filter(pk=self.file.pk).count(), 0)
        self.assertEqual(response.status_code, 204)
