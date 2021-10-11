from apps.files.models.permission_for_folder import PermissionForFolder
from apps.static.permissions import PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
from apps.files.serializers import PermissionForFolderSerializer, PermissionForFolderNestedSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import viewsets, status


class PermissionForFolderViewSet(viewsets.ModelViewSet):
    queryset = PermissionForFolder.objects.all()
    serializer_class = PermissionForFolderSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC):
            raise PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(PermissionForFolderNestedSerializer(instance=instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC):
            raise PermissionDenied()

        return super().destroy(request, *args, **kwargs)
