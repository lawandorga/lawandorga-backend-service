import base64
import mimetypes
import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from backend.static.encrypted_storage import EncryptedStorage
from backend.files.serializers import FileSerializer, FileCreateSerializer
from backend.files.models.file import File
from rest_framework import viewsets


class FileViewSet(viewsets.ModelViewSet):
    instance: File
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return FileCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.folder.user_has_permission_read(request.user):
            raise PermissionDenied()

        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlcs_aes_key(private_key_user)
        instance.download(aes_key)

        file = default_storage.open(instance.key)
        response = FileResponse(file, content_type=mimetypes.guess_type(instance.key)[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        # os.remove(instance.key)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlcs_aes_key(private_key_user)
        file = request.FILES['file']
        local_file = default_storage.save(self.instance.key, file)
        local_file_path = os.path.join(settings.MEDIA_ROOT, local_file)
        EncryptedStorage.encrypt_file_and_upload_to_s3(local_file_path, aes_key, self.instance.key)
        return response
