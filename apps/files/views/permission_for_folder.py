from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.core.static import PERMISSION_FILES_MANAGE_PERMISSIONS
from apps.files.models.permission_for_folder import PermissionForFolder
from apps.files.serializers import (
    PermissionForFolderNestedSerializer,
    PermissionForFolderSerializer,
)
from apps.static.permission import CheckPermissionWall


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
