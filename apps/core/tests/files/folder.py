from django.test import TestCase
from rest_framework.test import force_authenticate

from apps.core.models import Folder
from .file import FileTestsBase
from apps.core.views import FolderViewSet


class FolderTests(FileTestsBase, TestCase):
    def setup_folder(self):
        parent = Folder.objects.get(parent=None, rlc=self.rlc)
        self.folder = Folder.objects.create(
            name="Test Folder", rlc=self.rlc, parent=parent
        )

    def test_create_folder(self):
        view = FolderViewSet.as_view(actions={"post": "create"})
        data = {"name": "Test"}
        request = self.factory.post("", data)
        force_authenticate(request, self.user)
        response = view(request)
        self.assertContains(response, "Test", status_code=201)

    def test_update_folder(self):
        self.setup_folder()
        view = FolderViewSet.as_view(actions={"patch": "update"})
        data = {"name": "Test"}
        request = self.factory.patch("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.folder.pk)
        self.assertContains(response, "Test", status_code=200)

    def test_delete_folder(self):
        self.setup_folder()
        view = FolderViewSet.as_view(actions={"delete": "destroy"})
        data = {"name": "Test"}
        request = self.factory.delete("", data)
        force_authenticate(request, self.user)
        response = view(request, pk=self.folder.pk)
        self.assertEqual(response.status_code, 204)
