from rest_framework import serializers

from core.models import FolderPermission


class FolderPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolderPermission
        fields = "__all__"
