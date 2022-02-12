from apps.api.models.has_permission import HasPermission
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from apps.static.permission import CheckPermissionWall
from apps.api.serializers import OldHasPermissionSerializer, HasPermissionAllNamesSerializer, \
    HasPermissionNameSerializer
from django.db.models import Q
from apps.api.static import PERMISSION_ADMIN_MANAGE_PERMISSIONS, \
    get_all_collab_permissions, get_all_files_permissions, get_all_records_permissions, get_all_admin_permissions
from apps.api.models import Permission
from rest_framework import status, mixins


class HasPermissionViewSet(CheckPermissionWall, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, GenericViewSet):
    queryset = HasPermission.objects.all()
    serializer_class = OldHasPermissionSerializer
    permission_wall = {
        'create': PERMISSION_ADMIN_MANAGE_PERMISSIONS,
        'destroy': PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    }

    def create(self, request, *args, **kwargs):
        if 'group_has_permission' not in request.data:
            request.data.update({'group_has_permission': None})
        if 'user_has_permission' not in request.data:
            request.data.update({'user_has_permission': None})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        has_permission = HasPermission.objects.get(**serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(HasPermissionAllNamesSerializer(instance=has_permission).data, status=status.HTTP_201_CREATED,
                        headers=headers)

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
