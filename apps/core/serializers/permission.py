from rest_framework import serializers

from apps.core.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class PermissionNameSerializer(PermissionSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name"]
