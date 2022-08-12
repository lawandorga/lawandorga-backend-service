from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.models import HasPermission

from .group import GroupNameSerializer
from .permission import PermissionNameSerializer
from .user import UserProfileNameSerializer


class HasPermissionSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    permission_object = PermissionNameSerializer(read_only=True, source="permission")
    user_object = UserProfileNameSerializer(
        read_only=True, source="user_has_permission"
    )
    group_object = GroupNameSerializer(read_only=True, source="group_has_permission")

    class Meta:
        model = HasPermission
        fields = "__all__"

    def get_source(self, obj):
        if obj.user_has_permission and not obj.group_has_permission:
            return "USER"
        if not obj.user_has_permission and obj.group_has_permission:
            return "GROUP"
        return "ERROR"


class HasPermissionCreateSerializer(HasPermissionSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user_has_permission"].queryset = self.context[
            "request"
        ].user.rlc.rlc_members.all()
        self.fields["group_has_permission"].queryset = self.context[
            "request"
        ].user.rlc.group_from_rlc.all()

    def validate(self, data):
        user = data["user_has_permission"] if "user_has_permission" in data else None
        group = data["group_has_permission"] if "group_has_permission" in data else None
        permission = data["permission"] if "permission" in data else None

        if user is None and group is None:
            raise ValidationError("A permission needs an user or a group.")

        if (
            user
            and HasPermission.objects.filter(
                user_has_permission=user, permission=permission
            ).exists()
        ) or (
            group
            and HasPermission.objects.filter(
                group_has_permission=group, permission=permission
            ).exists()
        ):
            raise ValidationError("This permission exists already.")

        return data
