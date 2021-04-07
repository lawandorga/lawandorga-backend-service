#  law&orga - record and organization management software for refugee law clinics
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
from backend.api.models.group import Group
from backend.api.models.has_permission import HasPermission
from backend.api.models.permission import Permission
from backend.static import error_codes
from backend.static.permissions import (
    PERMISSION_MANAGE_PERMISSIONS_RLC,
    get_record_encryption_keys_permissions,
)
from backend.api.models import UserProfile, Rlc
from backend.api.serializers import (
    HasPermissionSerializer,
    UserProfileNameSerializer,
    GroupSerializer,
)
from backend.recordmanagement.helpers import check_encryption_key_holders_and_grant
from backend.static.middleware import get_private_key_from_request


class HasPermissionViewSet(viewsets.ModelViewSet):
    queryset = HasPermission.objects.all()
    serializer_class = HasPermissionSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        if "pk" not in kwargs:
            raise CustomError(error_codes.ERROR__API__ID_NOT_PROVIDED)
        try:
            hasPermission = HasPermission.objects.get(pk=kwargs["pk"])
        except:
            raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)

        if hasPermission.permission_for_rlc is not None:
            rlc = hasPermission.permission_for_rlc
        else:
            rlc = request.user.rlc

        if not request.user.has_permission(
            PERMISSION_MANAGE_PERMISSIONS_RLC, for_rlc=rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        hasPermission.delete()
        return Response({"status": "success"})

    def create(self, request, *args, **kwargs):
        data = request.data

        if "permission_for_rlc" in data:
            try:
                rlc = Rlc.objects.get(pk=data["permission_for_rlc"])
            except:
                raise CustomError(error_codes.ERROR__API__ID_NOT_FOUND)
        else:
            rlc = request.user.rlc

        if not request.user.is_superuser and not request.user.has_permission(
            PERMISSION_MANAGE_PERMISSIONS_RLC, for_rlc=rlc
        ):
            raise CustomError(error_codes.ERROR__API__PERMISSION__INSUFFICIENT)

        # can be removed?
        if HasPermission.already_existing(data):
            raise CustomError(error_codes.ERROR__API__HAS_PERMISSION__ALREADY_EXISTING)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        permission = Permission.objects.get(id=request.data["permission"])
        if permission in get_record_encryption_keys_permissions():
            granting_users_private_key = get_private_key_from_request(request)
            check_encryption_key_holders_and_grant(
                request.user, granting_users_private_key
            )
        # check if permission in rec enc perms TODO: this would be more performant
        # get users private key
        # if rlc -> add rec enc for all rlc users
        # if group -> add for all group members
        # if user -> add for user

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class HasPermissionStaticsViewSet(APIView):
    def get(self, response):
        if response.user.is_superuser:
            users = UserProfile.objects.all()
            groups = Group.objects.all()
        else:
            users = UserProfile.objects.filter(rlc=response.user.rlc, is_active=True)
            groups = Group.objects.filter(from_rlc=response.user.rlc)
        data = {
            "users": UserProfileNameSerializer(users, many=True).data,
            "groups": GroupSerializer(groups, many=True).data,
        }
        return Response(data)


class UserHasPermissionsViewSet(APIView):
    def get(self, request):
        user_permissions = [
            model_to_dict(perm) for perm in request.user.get_all_user_permissions()
        ]
        return Response({"user_permissions": user_permissions})
