from apps.api.models.has_permission import HasPermission
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from apps.static.permission import CheckPermissionWall
from apps.api.serializers import HasPermissionCreateSerializer, \
    HasPermissionNameSerializer, HasPermissionListSerializer, HasPermissionSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from apps.api.static import PERMISSION_ADMIN_MANAGE_PERMISSIONS, \
    get_all_collab_permissions, get_all_files_permissions, get_all_records_permissions, get_all_admin_permissions
from apps.api.models import Permission, UserProfile
from rest_framework import mixins


class HasPermissionViewSet(CheckPermissionWall, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, GenericViewSet):
    queryset = HasPermission.objects.none()
    serializer_class = HasPermissionSerializer
    permission_wall = {
        'list': PERMISSION_ADMIN_MANAGE_PERMISSIONS,
        'create': PERMISSION_ADMIN_MANAGE_PERMISSIONS,
        'destroy': PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    }

    def get_serializer_class(self):
        if self.action in ['list']:
            return HasPermissionListSerializer
        elif self.action in ['create']:
            return HasPermissionCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        rlc = self.request.user.rlc
        queryset = HasPermission.objects.filter(Q(user_has_permission__rlc=rlc) | Q(group_has_permission__from_rlc=rlc))
        queryset = queryset.select_related('permission', 'group_has_permission', 'user_has_permission')
        # user param like ?user=5
        user = self.request.query_params.get('user', None)
        if user is not None:
            user = get_object_or_404(UserProfile, pk=user)
            groups = user.rlcgroups.all()
            queryset = queryset.filter(Q(user_has_permission=user) | Q(group_has_permission__in=groups))
        # group param like ?group=3
        group = self.request.query_params.get('group', None)
        if group is not None:
            queryset = queryset.filter(group_has_permission=group)
        return queryset

    def create(self, request, *args, **kwargs):
        if 'group_has_permission' not in request.data:
            request.data.update({'group_has_permission': None})
        if 'user_has_permission' not in request.data:
            request.data.update({'user_has_permission': None})
        return super().create(request, *args, **kwargs)

    def get_permissions_response(self, request, permissions):
        general_permissions = HasPermission.objects \
            .filter(permission__in=Permission.objects.filter(name__in=permissions)) \
            .filter(Q(user_has_permission__in=request.user.rlc.rlc_members.all()) |
                    Q(group_has_permission__in=request.user.rlc.group_from_rlc.all())) \
            .select_related('user_has_permission', 'group_has_permission', 'permission')
        return Response(HasPermissionNameSerializer(general_permissions, many=True).data)

    @action(detail=False, methods=['get'])
    def collab(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_collab_permissions())

    @action(detail=False, methods=['get'])
    def files(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_files_permissions())

    @action(detail=False, methods=['get'])
    def records(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_records_permissions())

    @action(detail=False, methods=['get'])
    def admin(self, request, *args, **kwargs):
        return self.get_permissions_response(request, get_all_admin_permissions())
