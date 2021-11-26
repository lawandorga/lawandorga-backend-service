from apps.collab.models import CollabPermission
from rest_framework import serializers


class CollabPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollabPermission
        fields = "__all__"


class CollabPermissionNameSerializer(CollabPermissionSerializer):
    class Meta:
        model = CollabPermission
        fields = ['name', 'id']
