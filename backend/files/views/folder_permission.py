from backend.files.models.folder_permission import FolderPermission
from backend.files.serializers import FolderPermissionSerializer
from rest_framework import viewsets


class FolderPermissionViewSet(viewsets.ModelViewSet):
    queryset = FolderPermission.objects.all()
    serializer_class = FolderPermissionSerializer
