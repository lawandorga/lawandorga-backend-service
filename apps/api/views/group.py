from rest_framework.exceptions import ParseError
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.static.permission import CheckPermissionWall
from rest_framework.request import Request
from apps.api.serializers import GroupSerializer, MemberIntegerSerializer, UserProfileSerializer, \
    OldHasPermissionNameSerializer, GroupCreateSerializer
from apps.api.static import PERMISSION_ADMIN_MANAGE_GROUPS
from apps.api.models import Group, RlcUser
from rest_framework import viewsets, status


class GroupViewSet(CheckPermissionWall, viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_wall = {
        'create': PERMISSION_ADMIN_MANAGE_GROUPS,
        'update': PERMISSION_ADMIN_MANAGE_GROUPS,
        'partial_update': PERMISSION_ADMIN_MANAGE_GROUPS,
        'destroy': PERMISSION_ADMIN_MANAGE_GROUPS,
        'member': PERMISSION_ADMIN_MANAGE_GROUPS,
    }

    def get_queryset(self):
        return Group.objects.filter(from_rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ['create']:
            return GroupCreateSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['get'])
    def members(self, *args, **kwargs):
        group = self.get_object()
        members = group.group_members.all()
        return Response(UserProfileSerializer(members, many=True).data)

    @action(detail=True, methods=['get'])
    def permissions(self, *args, **kwargs):
        group = self.get_object()
        permissions = group.group_has_permission.all()
        return Response(OldHasPermissionNameSerializer(permissions, many=True).data)

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
            group.group_members.add(member)
            return Response(UserProfileSerializer(member).data, status=status.HTTP_200_OK)

        # remove member from group
        if request.method == "DELETE":
            group.group_members.remove(member)
            return Response(status.HTTP_200_OK)

        # return something
        raise ParseError('This request needs to be POST or DELETE.')
