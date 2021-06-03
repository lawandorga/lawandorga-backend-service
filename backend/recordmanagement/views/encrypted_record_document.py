from backend.recordmanagement.models.encrypted_record_document import EncryptedRecordDocument
from backend.recordmanagement.serializers import RecordDocumentSerializer, RecordDocumentCreateSerializer
from backend.static.encrypted_storage import EncryptedStorage
from rest_framework.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from rest_framework.request import Request
from rest_framework import viewsets
from backend.static import permissions
from django.conf import settings
from django.http import FileResponse
import mimetypes
import os


class EncryptedRecordDocumentViewSet(viewsets.ModelViewSet):
    queryset = EncryptedRecordDocument.objects.none()
    serializer_class = RecordDocumentSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return RecordDocumentCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return EncryptedRecordDocument.objects.filter(record__from_rlc=self.request.user.rlc)

    def retrieve(self, request: Request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_VIEW_RECORDS_RLC):
            raise PermissionDenied()

        instance = self.get_object()

        if not instance.record.user_has_permission(request.user):
            raise PermissionDenied()

        private_key_user = request.user.get_private_key(request=request)
        record_key = instance.record.get_decryption_key(request.user, private_key_user)
        instance.download(record_key)

        file = default_storage.open(instance.get_key())
        response = FileResponse(file, content_type=mimetypes.guess_type(instance.get_file_key())[0])
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(instance.name)
        return response

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_VIEW_RECORDS_RLC):
            raise PermissionDenied()

        response = super().create(request, *args, **kwargs)
        file = request.FILES['file']
        local_file = default_storage.save(self.instance.get_key(), file)
        local_file_path = os.path.join(settings.MEDIA_ROOT, local_file)
        private_key_user = request.user.get_private_key(request=request)
        record_key = self.instance.record.get_decryption_key(request.user, private_key_user)
        EncryptedStorage.encrypt_file_and_upload_to_s3(local_file_path, record_key, self.instance.get_key())
        default_storage.delete(self.instance.get_key())
        default_storage.delete(self.instance.get_file_key())
        return response
