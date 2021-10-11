from apps.recordmanagement.models.encrypted_record_permission import EncryptedRecordPermission
from apps.recordmanagement.models.record_encryption import RecordEncryption
from apps.recordmanagement.serializers import EncryptedRecordPermissionSerializer
from apps.api.models.notification import Notification
from rest_framework.exceptions import PermissionDenied
from apps.static.encryption import RSAEncryption
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from apps.static import permissions
from django.utils import timezone


class EncryptedRecordPermissionProcessViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    model = EncryptedRecordPermission
    queryset = EncryptedRecordPermission.objects.none()
    serializer_class = EncryptedRecordPermissionSerializer

    def get_queryset(self):
        return EncryptedRecordPermission.objects.filter(record__from_rlc=self.request.user.rlc)

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.request_processed = request.user
        instance.processed_on = timezone.now()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['state'] == "gr":
            private_key_user = request.user.get_private_key(request=request)
            record_key = instance.record.get_decryption_key(request.user, private_key_user)
            public_key_user = instance.request_from.get_public_key()
            encrypted_record_key = RSAEncryption.encrypt(record_key, public_key_user)
            data = {
                'user': instance.request_from,
                'record': instance.record,
                'encrypted_key': encrypted_record_key,
            }
            if not RecordEncryption.objects.filter(user=data['user'], record=data['record']).exists():
                RecordEncryption.objects.create(**data)
            Notification.objects.notify_record_permission_accepted(
                request.user, instance
            )
        elif serializer.validated_data['state'] == "de":
            Notification.objects.notify_record_permission_declined(request.user, instance)

        serializer.save()
        return Response(serializer.data)

