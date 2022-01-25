from apps.api.models.has_permission import HasPermission
from rest_framework.exceptions import ValidationError
from apps.api.serializers import GroupNameSerializer, UserProfileNameSerializer, PermissionSerializer
from rest_framework import serializers


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
        user = data['user_has_permission'] if 'user_has_permission' in data else None
        group = data['group_has_permission'] if 'group_has_permission' in data else None
        permission = data['permission'] if 'permission' in data else None

        if user is None and group is None:
            raise ValidationError('A permission needs an user or a group.')

        if (
            (user and HasPermission.objects.filter(user_has_permission=user, permission=permission).exists()) or
            (group and HasPermission.objects.filter(group_has_permission=group, permission=permission).exists())
        ):
            raise ValidationError('This permission exists already.')

        return data


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
    permission = PermissionSerializer(read_only=True)
