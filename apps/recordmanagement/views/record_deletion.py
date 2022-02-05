from apps.recordmanagement.models.record_deletion import RecordDeletion
from apps.recordmanagement.serializers import RecordDeletionSerializer
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import viewsets
from apps.api import static


class RecordDeletionViewSet(viewsets.ModelViewSet):
    serializer_class = RecordDeletionSerializer
    queryset = RecordDeletion.objects.none()

    def get_queryset(self):
        return RecordDeletion.objects.filter(
            Q(requested_by__rlc=self.request.user.rlc) |
            Q(processed_by__rlc=self.request.user.rlc) |
            Q(record__template__rlc=self.request.user.rlc)
        )

    def list(self, request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.has_permission(permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS):
            raise PermissionDenied()
        return super().update(request, *args, **kwargs)
