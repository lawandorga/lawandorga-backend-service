from apps.static.permissions import PERMISSION_VIEW_PERMISSIONS_RLC
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework.response import Response
from apps.api.errors import CustomError
from apps.static import error_codes
from .. import serializers
from apps.api.models.permission import Permission


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionNameSerializer

    def retrieve(self, request, *args, **kwargs):
        if "pk" not in kwargs:
            raise CustomError(error_codes.ERROR__API__MISSING_ARGUMENT)
        try:
            permission = Permission.objects.get(pk=kwargs["pk"])
        except:
            raise CustomError(error_codes.ERROR__API__PERMISSION__NOT_FOUND)

        if not request.user.has_permission(
            PERMISSION_VIEW_PERMISSIONS_RLC, for_rlc=request.user.rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        user_permissions = [
            model_to_dict(has_permission)
            for has_permission in permission.get_users_with_permission_from_rlc(
                request.user.rlc
            )
        ]
        group_permissions = [
            model_to_dict(has_permission)
            for has_permission in permission.get_groups_with_permission_from_rlc(
                request.user.rlc
            )
        ]

        data = serializers.PermissionSerializer(permission).data

        data.update(
            {"has_permissions": user_permissions + group_permissions}
        )
        return Response(data)
