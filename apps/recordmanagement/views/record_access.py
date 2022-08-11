from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.response import Response

from apps.core.static import PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS
from apps.recordmanagement.models import RecordEncryptionNew
from apps.recordmanagement.models.record_access import RecordAccess
from apps.recordmanagement.serializers import RecordAccessSerializer
from apps.static.encryption import RSAEncryption
from apps.static.permission import CheckPermissionWall


class RecordAccessViewSet(
    CheckPermissionWall,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = RecordAccess.objects.none()
    serializer_class = RecordAccessSerializer
    permission_wall = {
        "list": PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
        "update": PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
        "partial_update": PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS,
    }

    def get_queryset(self):
        return RecordAccess.objects.filter(record__template__rlc=self.request.user.rlc)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            **request.data,
            "processed_by": request.user.id,
            "processed_on": timezone.now(),
        }
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["state"] == "gr":
            private_key_user = request.user.get_private_key(request=request)
            try:
                record_key = instance.record.get_aes_key(
                    user=request.user, private_key_user=private_key_user
                )
            except ObjectDoesNotExist:
                raise PermissionDenied(
                    "You have no access to this record. Therefore you can not allow access to this record."
                )
            public_key_user = instance.requested_by.get_public_key()
            encrypted_record_key = RSAEncryption.encrypt(record_key, public_key_user)
            data = {
                "user": instance.requested_by,
                "record": instance.record,
                "key": encrypted_record_key,
            }
            if not RecordEncryptionNew.objects.filter(
                user=data["user"], record=data["record"]
            ).exists():
                RecordEncryptionNew.objects.create(**data)
        elif serializer.validated_data["state"] == "de":
            pass

        serializer.save()
        return Response(serializer.data)
