from django.db.models import Q
from rest_framework import mixins, viewsets

from core.records.models import RecordDeletion
from core.records.serializers import RecordDeletionSerializer
from core.seedwork.permission import CheckPermissionWall
from core.static import PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS


class RecordDeletionViewSet(
    CheckPermissionWall,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RecordDeletionSerializer
    queryset = RecordDeletion.objects.none()
    permission_wall = {
        "list": PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
        "update": PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
        "partial_update": PERMISSION_ADMIN_MANAGE_RECORD_DELETION_REQUESTS,
    }

    def get_queryset(self):
        return RecordDeletion.objects.filter(
            Q(requested_by__rlc_user__org=self.request.user.rlc)
            | Q(processed_by__rlc_user__org=self.request.user.rlc)
            | Q(record__template__rlc=self.request.user.rlc)
        )
