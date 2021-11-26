from apps.api.models.has_permission import HasPermission
from apps.api.serializers import GroupNameSerializer, UserProfileNameSerializer, PermissionNameSerializer
from rest_framework import serializers
from ..errors import EntryAlreadyExistingError


class HasPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HasPermission
        fields = '__all__'


class OldHasPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HasPermission
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_has_permission'].queryset = self.context['request'].user.rlc.rlc_members.all()
        self.fields['group_has_permission'].queryset = self.context['request'].user.rlc.group_from_rlc.all()

    def validate(self, data):
        if HasPermission.validate_values(data):
            return data
        raise serializers.ValidationError("validationError at creating has_permission")

    def create(self, validated_data):
        if HasPermission.already_existing(validated_data):
            raise EntryAlreadyExistingError("entry already exists")
        return super().create(validated_data)


class OldHasPermissionNameSerializer(HasPermissionSerializer):
    name = serializers.SerializerMethodField(method_name='get_name')

    def get_name(self, obj):
        return obj.permission.name


class HasPermissionAllNamesSerializer(HasPermissionSerializer):
    name = serializers.SerializerMethodField(method_name='get_name')
    user_has_permission = UserProfileNameSerializer(read_only=True)
    group_has_permission = GroupNameSerializer(read_only=True)

    def get_name(self, obj):
        return obj.permission.name


class HasPermissionNameSerializer(HasPermissionSerializer):
    user_has_permission = UserProfileNameSerializer(read_only=True)
    group_has_permission = GroupNameSerializer(read_only=True)
    permission = PermissionNameSerializer(read_only=True)
