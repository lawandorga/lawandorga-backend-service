from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ...auth.models import RlcUser
from ..models import HasPermission
from .group import GroupNameSerializer
from .permission import PermissionNameSerializer


class RlcUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RlcUser
        fields = ("id", "name", "email")


class HasPermissionSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()  # type: ignore
    permission_object = PermissionNameSerializer(read_only=True, source="permission")
    user_object = RlcUserSerializer(read_only=True, source="user")
    group_object = GroupNameSerializer(read_only=True, source="group_has_permission")

    class Meta:
        model = HasPermission
        fields = "__all__"

    def get_source(self, obj):
        if obj.user and not obj.group_has_permission:
            return "USER"
        if not obj.user and obj.group_has_permission:
            return "GROUP"
        return "ERROR"


class HasPermissionCreateSerializer(HasPermissionSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group_has_permission"].queryset = self.context[
            "request"
        ].user.rlc.group_from_rlc.all()

    def validate(self, data):
        data["user"] = None
        group = data["group_has_permission"] if "group_has_permission" in data else None
        permission = data["permission"] if "permission" in data else None

        if group is None:
            raise ValidationError("A permission needs an user or a group.")

        if (
            group
            and HasPermission.objects.filter(
                group_has_permission=group, permission=permission
            ).exists()
        ):
            raise ValidationError("This permission exists already.")

        return data
