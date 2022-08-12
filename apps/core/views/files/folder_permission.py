from rest_framework import viewsets

from apps.core.models import FolderPermission
from apps.core.serializers import FolderPermissionSerializer


class FolderPermissionViewSet(viewsets.ModelViewSet):
    queryset = FolderPermission.objects.all()
    serializer_class = FolderPermissionSerializer
