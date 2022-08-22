from rest_framework import serializers

from apps.core.models import FolderPermission


class FolderPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderPermission
        fields = "__all__"
