from apps.api.models.permission import Permission
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class PermissionNameSerializer(PermissionSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']
