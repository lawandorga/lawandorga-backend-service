from apps.api.models.has_permission import HasPermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from apps.static.permissions import PERMISSION_MANAGE_PERMISSIONS_RLC, \
    get_all_collab_permissions, get_all_files_permissions, get_all_records_permissions
from rest_framework.response import Response
from apps.api.serializers import OldHasPermissionSerializer, HasPermissionAllNamesSerializer, \
    HasPermissionNameSerializer
from django.db.models import Q
from apps.api.models import Permission
from rest_framework import status
from rest_framework import viewsets


class HasPermissionViewSet(viewsets.ModelViewSet):
    queryset = HasPermission.objects.all()
    serializer_class = OldHasPermissionSerializer

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_PERMISSIONS_RLC):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_PERMISSIONS_RLC):
            raise PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        has_permission = HasPermission.objects.get(**serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(HasPermissionAllNamesSerializer(instance=has_permission).data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=False, methods=['get'])
    def collab(self, request, *args, **kwargs):
        general_permissions = HasPermission.objects \
            .filter(permission__in=Permission.objects.filter(name__in=get_all_collab_permissions())) \
            .filter(Q(user_has_permission__in=request.user.rlc.rlc_members.all()) |
                    Q(group_has_permission__in=request.user.rlc.group_from_rlc.all())) \
            .select_related('user_has_permission', 'group_has_permission', 'permission')
        return Response(HasPermissionNameSerializer(general_permissions, many=True).data)

    @action(detail=False, methods=['get'])
    def files(self, request, *args, **kwargs):
        general_permissions = HasPermission.objects \
            .filter(permission__in=Permission.objects.filter(name__in=get_all_files_permissions())) \
            .filter(Q(user_has_permission__in=request.user.rlc.rlc_members.all()) |
                    Q(group_has_permission__in=request.user.rlc.group_from_rlc.all())) \
            .select_related('user_has_permission', 'group_has_permission', 'permission')
        return Response(HasPermissionNameSerializer(general_permissions, many=True).data)

    @action(detail=False, methods=['get'])
    def records(self, request, *args, **kwargs):
        general_permissions = HasPermission.objects \
            .filter(permission__in=Permission.objects.filter(name__in=get_all_records_permissions())) \
            .filter(Q(user_has_permission__in=request.user.rlc.rlc_members.all()) |
                    Q(group_has_permission__in=request.user.rlc.group_from_rlc.all())) \
            .select_related('user_has_permission', 'group_has_permission', 'permission')
        return Response(HasPermissionNameSerializer(general_permissions, many=True).data)
