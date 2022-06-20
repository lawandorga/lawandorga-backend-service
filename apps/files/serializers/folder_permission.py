from rest_framework import serializers

from apps.files.models.folder_permission import FolderPermission


class FolderPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderPermission
        fields = "__all__"
