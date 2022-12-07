from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.records.models import RecordAccess
from core.records.serializers import RecordAccessSerializer
from core.seedwork.permission import CheckPermissionWall
from core.static import PERMISSION_ADMIN_MANAGE_RECORD_ACCESS_REQUESTS


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
                instance.record.get_aes_key(
                    user=request.user.rlc_user, private_key_user=private_key_user
                )
            except ObjectDoesNotExist:
                raise PermissionDenied(
                    "You have no access to this record. Therefore you can not allow access to this record."
                )
            instance.record.grant_access(
                instance.requested_by.rlc_user, request.user.rlc_user
            )

        serializer.save()
        return Response(serializer.data)
