from rest_framework import viewsets

from apps.files.models.folder_permission import FolderPermission
from apps.files.serializers import FolderPermissionSerializer


class FolderPermissionViewSet(viewsets.ModelViewSet):
    queryset = FolderPermission.objects.all()
    serializer_class = FolderPermissionSerializer
