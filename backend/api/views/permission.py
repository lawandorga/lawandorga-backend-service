#  rlcapp - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>

from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.static import error_codes
from backend.static.permissions import PERMISSION_VIEW_PERMISSIONS_RLC
from .. import models, serializers


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = models.Permission.objects.all()
    serializer_class = serializers.PermissionNameSerializer

    def retrieve(self, request, *args, **kwargs):
        if 'pk' not in kwargs:
            raise CustomError(error_codes.ERROR__API__MISSING_ARGUMENT)
        try:
            permission = models.Permission.objects.get(pk=kwargs['pk'])
        except:
            raise CustomError(error_codes.ERROR__API__PERMISSION__NOT_FOUND)

        if not request.user.has_permission(PERMISSION_VIEW_PERMISSIONS_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        user_permissions = [model_to_dict(has_permission) for has_permission in
                            permission.get_users_with_permission_from_rlc(request.user.rlc)]
        group_permissions = [model_to_dict(has_permission) for has_permission in
                             permission.get_groups_with_permission_from_rlc(request.user.rlc)]
        rlc_permissions = [model_to_dict(has_permission) for has_permission in
                           permission.get_rlc_permissions_with_special_permission(request.user.rlc)]

        data = serializers.PermissionSerializer(permission).data

        data.update({
            'has_permissions': user_permissions + group_permissions + rlc_permissions
        })
        return Response(data)


class PermissionsForGroupViewSet(APIView):
    def get(self, request, pk):
        try:
            group = models.Group.objects.get(pk=pk)
        except:
            raise CustomError(error_codes.ERROR__API__GROUP__GROUP_NOT_FOUND)

        if not request.user.has_permission(PERMISSION_VIEW_PERMISSIONS_RLC, for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        data = [model_to_dict(has_permission) for has_permission in
                models.HasPermission.objects.filter(group_has_permission=group)]

        return Response(data)
