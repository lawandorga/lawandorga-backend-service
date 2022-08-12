from rest_framework import mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.core.models import PermissionForCollabDocument
from apps.core.static import PERMISSION_COLLAB_MANAGE_PERMISSIONS

from ...serializers import PermissionForCollabDocumentSerializer
from .collab_document import PermissionForCollabDocumentAllNamesSerializer


class PermissionForCollabDocumentViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet
):
    queryset = PermissionForCollabDocument.objects.all()
    serializer_class = PermissionForCollabDocumentSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_COLLAB_MANAGE_PERMISSIONS):
            raise PermissionDenied()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance = PermissionForCollabDocument.objects.get(pk=serializer.data["id"])
        data = PermissionForCollabDocumentAllNamesSerializer(instance).data
        return Response(data=data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_COLLAB_MANAGE_PERMISSIONS):
            raise PermissionDenied()
        return super().destroy(request, *args, **kwargs)
