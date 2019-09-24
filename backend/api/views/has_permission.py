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

from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.forms.models import model_to_dict

from backend.api.errors import CustomError
from backend.static import error_codes
from backend.static.permissions import PERMISSION_MANAGE_PERMISSIONS_RLC
from ..models import HasPermission, Group, UserProfile
from ..serializers import HasPermissionSerializer, GroupNameSerializer, UserProfileNameSerializer


class HasPermissionViewSet(viewsets.ModelViewSet):
    queryset = HasPermission.objects.all()
    serializer_class = HasPermissionSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        if 'pk' not in kwargs:
            raise CustomError(error_codes.ERROR__API__HAS_PERMISSION__NO_ID_PROVIDED)
        try:
            hasPermission = HasPermission.objects.get(pk=kwargs['pk'])
        except:
            raise CustomError(error_codes.ERROR__API__HAS_PERMISSION__NOT_FOUND)

        user = request.user
        if not user.has_permission(PERMISSION_MANAGE_PERMISSIONS_RLC, for_rlc=user.rlc):
            return CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        hasPermission.delete()
        return Response({'status': 'success'})

    # def create(self, request, *args, **kwargs) -> Response:
    #     if not request.user.has_permission(PERMISSION_MANAGE_PERMISSIONS_RLC, for_rlc=request.user.rlc):
    #         raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
    #
    #     a = 10
    #     pass

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.has_permission(PERMISSION_MANAGE_PERMISSIONS_RLC,
                                                                             for_rlc=request.user.rlc):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)
        # if request.data['rlc_has_permission'] and request.user.rlc.id != request.data['rlc_has_permission'] or \
        #     request.data['permission_for_rlc'] and request.user.rlc.id != request.data['permission_for_rlc']:
        #     raise CustomError(error_codes.ERROR__API__HAS_PERMISSION__CAN_NOT_CREATE)
        if HasPermission.already_existing(request.data):
            raise CustomError(error_codes.ERROR__API__HAS_PERMISSION__ALREADY_EXISTING)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class HasPermissionStaticsViewSet(APIView):
    def get(self, response):
        if response.user.is_superuser:
            users = UserProfile.objects.all()
            groups = Group.objects.all()
        else:
            users = UserProfile.objects.filter(rlc=response.user.rlc, is_active=True)
            groups = Group.objects.filter(from_rlc=response.user.rlc)
        data = {
            'users': UserProfileNameSerializer(users, many=True).data,
            'groups': GroupNameSerializer(groups, many=True).data
        }
        return Response(data)


class UserHasPermissionsViewSet(APIView):
    def get(self, request):
        user_permissions = [model_to_dict(perm) for perm in request.user.get_all_user_permissions()]
        return Response({
            'user_permissions': user_permissions
        })
