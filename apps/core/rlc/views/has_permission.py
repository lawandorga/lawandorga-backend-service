from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.core.models import HasPermission, Permission, UserProfile
from apps.core.static import (
    PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    get_all_admin_permissions,
    get_all_collab_permissions,
    get_all_files_permissions,
    get_all_records_permissions,
)
from apps.core.seedwork.permission import CheckPermissionWall

from ..serializers import HasPermissionCreateSerializer, HasPermissionSerializer


class HasPermissionViewSet(
    CheckPermissionWall,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = HasPermission.objects.none()
    serializer_class = HasPermissionSerializer
    permission_wall = {
        "list": PERMISSION_ADMIN_MANAGE_PERMISSIONS,
        "create": PERMISSION_ADMIN_MANAGE_PERMISSIONS,
        "destroy": PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    }

    def get_serializer_class(self):
        if self.action in ["create"]:
            return HasPermissionCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        rlc = self.request.user.rlc_user.org
        queryset = HasPermission.objects.filter(
            Q(user__org=rlc) | Q(group_has_permission__from_rlc=rlc)
        )
        queryset = queryset.select_related("permission", "group_has_permission", "user")
        # user param like ?user=5
        user = self.request.query_params.get("user", None)
        if user is not None:
            user = get_object_or_404(UserProfile, pk=user)
            groups = user.rlc_user.groups.all()
            queryset = queryset.filter(
                Q(user=user.rlc_user) | Q(group_has_permission__in=groups)
            )
        # group param like ?group=3
        group = self.request.query_params.get("group", None)
        if group is not None:
            queryset = queryset.filter(group_has_permission__pk=group)
        return queryset

    def create(self, request, *args, **kwargs):
        if "group_has_permission" not in request.data:
            request.data.update({"group_has_permission": None})
        request.data.update({"user": None})
        return super().create(request, *args, **kwargs)

    def get_permissions_response(self, request, permissions):
        general_permissions = (
            HasPermission.objects.filter(
                permission__in=Permission.objects.filter(name__in=permissions)
            )
            .filter(
                Q(user__in=request.user.rlc.users.all())
                | Q(group_has_permission__in=request.user.rlc.group_from_rlc.all())
            )
            .select_related("user", "group_has_permission", "permission")
        )
        return Response(HasPermissionSerializer(general_permissions, many=True).data)

    @action(detail=False, methods=["get"])
    def collab(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_collab_permissions())

    @action(detail=False, methods=["get"])
    def files(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_files_permissions())

    @action(detail=False, methods=["get"])
    def records(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_records_permissions())

    @action(detail=False, methods=["get"])
    def admin(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_admin_permissions())
