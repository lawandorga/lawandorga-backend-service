from backend.files.models.folder_permission import FolderPermission
from rest_framework import serializers


class FolderPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderPermission
        fields = "__all__"
