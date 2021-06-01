import base64
import os

from django.core.files.storage import default_storage
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
        instance.download(aes_key, instance.key)

        encoded_file = base64.b64encode(open(instance.key, "rb").read())
        res = Response(encoded_file, content_type="application/zip")
        res["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        os.remove(instance.key)
        return res

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        private_key_user = request.user.get_private_key(request=request)
        aes_key = request.user.get_rlcs_aes_key(private_key_user)
        file = request.FILES['file']
        local_file = default_storage.save(self.instance.key, file)
        EncryptedStorage.encrypt_file_and_upload_to_s3(local_file, aes_key, self.instance.key)
        return response
