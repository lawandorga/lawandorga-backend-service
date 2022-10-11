import mimetypes

from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from apps.core.models import UserProfile
from apps.core.records.models.encrypted_record_document import EncryptedRecordDocument
from apps.core.records.serializers import (
    RecordDocumentCreateSerializer,
    RecordDocumentSerializer,
)


class EncryptedRecordDocumentViewSet(viewsets.ModelViewSet):
    queryset = EncryptedRecordDocument.objects.none()
    serializer_class = RecordDocumentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return RecordDocumentCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return EncryptedRecordDocument.objects.filter(
            record__template__rlc=self.request.user.rlc
        )

    def retrieve(self, request: Request, *args, **kwargs):
        # instance
        instance = self.get_object()

        # check permission
        if not instance.record.encryptions.filter(user=request.user).exists():
            raise PermissionDenied()

        # download the file
        user: UserProfile = request.user  # type: ignore
        private_key_user = user.get_private_key(request=request)
        record_key = instance.record.get_aes_key(request.user, private_key_user)
        file = instance.download(record_key)

        # generate response
        response = FileResponse(
            file, content_type=mimetypes.guess_type(instance.get_key())[0]
        )
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            instance.name
        )

        # return
        return response

    def perform_create(self, serializer):
        self.instance = serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        file = request.FILES["file"]
        private_key_user = request.user.get_private_key(request=request)
        record_key = self.instance.record.get_aes_key(request.user, private_key_user)
        # upload the file to s3
        self.instance.upload(file, record_key)
        # return
        return response
