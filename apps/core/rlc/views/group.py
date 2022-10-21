from rest_framework import viewsets

from apps.core.models import Group
from apps.core.static import PERMISSION_ADMIN_MANAGE_GROUPS
from apps.seedwork.permission import CheckPermissionWall

from ..serializers import GroupCreateSerializer, GroupSerializer


class GroupViewSet(CheckPermissionWall, viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_wall = {
        "create": PERMISSION_ADMIN_MANAGE_GROUPS,
        "update": PERMISSION_ADMIN_MANAGE_GROUPS,
        "partial_update": PERMISSION_ADMIN_MANAGE_GROUPS,
        "destroy": PERMISSION_ADMIN_MANAGE_GROUPS,
    }

    def get_queryset(self):
        return Group.objects.filter(from_rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ["create"]:
            return GroupCreateSerializer
        return super().get_serializer_class()
