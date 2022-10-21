from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.core.models import PermissionForFolder
from apps.core.seedwork.permission import CheckPermissionWall
from apps.core.static import PERMISSION_FILES_MANAGE_PERMISSIONS

from ..serializers import (
    PermissionForFolderNestedSerializer,
    PermissionForFolderSerializer,
)


class PermissionForFolderViewSet(CheckPermissionWall, viewsets.ModelViewSet):
    queryset = PermissionForFolder.objects.all()
    serializer_class = PermissionForFolderSerializer
    permission_wall = {
        "create": PERMISSION_FILES_MANAGE_PERMISSIONS,
        "destroy": PERMISSION_FILES_MANAGE_PERMISSIONS,
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            PermissionForFolderNestedSerializer(instance=instance).data,
            status=status.HTTP_201_CREATED,
        )
