from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.models import Group, RlcUser
from apps.api.serializers import (GroupCreateSerializer, GroupSerializer,
                                  MemberIntegerSerializer,
                                  RlcUserForeignSerializer)
from apps.api.static import PERMISSION_ADMIN_MANAGE_GROUPS
from apps.static.permission import CheckPermissionWall


class GroupViewSet(CheckPermissionWall, viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_wall = {
        "create": PERMISSION_ADMIN_MANAGE_GROUPS,
        "update": PERMISSION_ADMIN_MANAGE_GROUPS,
        "partial_update": PERMISSION_ADMIN_MANAGE_GROUPS,
        "destroy": PERMISSION_ADMIN_MANAGE_GROUPS,
        "member": PERMISSION_ADMIN_MANAGE_GROUPS,
    }

    def get_queryset(self):
        return Group.objects.filter(from_rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ["create"]:
            return GroupCreateSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["post", "delete"])
    def member(self, request: Request, pk=None):
        # get the group
        group = self.get_object()

        # get the data
        serializer = MemberIntegerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = RlcUser.objects.get(pk=serializer.validated_data["member"]).user

        # add member to group
        if request.method == "POST":
            if member in group.group_members.all():
                raise ParseError(
                    {"member": ["This user is already part of the group."]}
                )
            group.group_members.add(member)
            return Response(
                RlcUserForeignSerializer(member.rlc_user).data,
                status=status.HTTP_200_OK,
            )

        # remove member from group
        if request.method == "DELETE":
            group.group_members.remove(member)
            return Response(status.HTTP_200_OK)

        # return something
        raise ParseError("This request needs to be POST or DELETE.")
