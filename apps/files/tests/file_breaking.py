from django.core.files.storage import default_storage
from apps.files.tests.file import FileTestsBase
from rest_framework.test import force_authenticate
from apps.files.models import File
from apps.files.views import FileViewSet
from django.test import TestCase
from django.conf import settings


settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'


class FileTestsBreaking(FileTestsBase, TestCase):
    def test_retrieve_file_not_on_server(self):
        # setup and delete the file for this test case to be like reality
        self.setup_file()
        default_storage.delete(self.file.file.name)
        # test case
        view = FileViewSet.as_view(actions={'get': 'retrieve'})
        request = self.factory.get('')
        force_authenticate(request, self.user)
        response = view(request, pk=self.file.pk)
        self.assertContains(response, 'The file could not be found', status_code=404)
        file = File.objects.get(pk=self.file.pk)
        self.assertEqual(file.exists, False)
        # clean up
        file.file.delete()

    def test_retrieve_file_with_no_name(self):
        # setup and unset file name to equal reality
        self.setup_file()
        self.file.file.name = ''
        self.file.save()
        # test case
        view = FileViewSet.as_view(actions={'get': 'retrieve'})
        request = self.factory.get('')
        force_authenticate(request, self.user)
        response = view(request, pk=self.file.pk)
        self.assertContains(response, 'The file could not be found', status_code=404)
        file = File.objects.get(pk=self.file.pk)
        self.assertEqual(file.exists, False)
        # clean up
        file.file.delete()
