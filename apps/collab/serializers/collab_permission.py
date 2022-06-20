from rest_framework import serializers

from apps.collab.models import CollabPermission


class CollabPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabPermission
        fields = "__all__"


class CollabPermissionNameSerializer(CollabPermissionSerializer):
    class Meta:
        model = CollabPermission
        fields = ["name", "id"]
