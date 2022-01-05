from apps.recordmanagement.models.record_access import RecordAccess
from apps.recordmanagement.serializers import RecordAccessSerializer
from apps.recordmanagement.models import RecordEncryptionNew
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from apps.static.encryption import RSAEncryption
from rest_framework import viewsets, mixins
from django.utils import timezone
from apps.static import permissions


class RecordAccessViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = RecordAccess.objects.none()
    serializer_class = RecordAccessSerializer

    def get_queryset(self):
        return RecordAccess.objects.filter(record__template__rlc=self.request.user.rlc)

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {**request.data, 'processed_by': request.user.id, 'processed_on': timezone.now()}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['state'] == "gr":
            private_key_user = request.user.get_private_key(request=request)
            try:
                record_key = instance.record.get_aes_key(user=request.user, private_key_user=private_key_user)
            except ObjectDoesNotExist:
                raise PermissionDenied(
                    'You have no access to this record. Therefore you can not allow access to this record.')
            public_key_user = instance.requested_by.get_public_key()
            encrypted_record_key = RSAEncryption.encrypt(record_key, public_key_user)
            data = {
                'user': instance.requested_by,
                'record': instance.record,
                'key': encrypted_record_key,
            }
            if not RecordEncryptionNew.objects.filter(user=data['user'], record=data['record']).exists():
                RecordEncryptionNew.objects.create(**data)
        elif serializer.validated_data['state'] == "de":
            pass

        serializer.save()
        return Response(serializer.data)
