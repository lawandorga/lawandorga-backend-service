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
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.forms.models import model_to_dict

from apps.api.errors import CustomError
from apps.api.models.group import Group
from apps.api.models.has_permission import HasPermission
from apps.api.models.permission import Permission
from apps.static import error_codes
from apps.static.permissions import (
    PERMISSION_MANAGE_PERMISSIONS_RLC,
    get_record_encryption_keys_permissions,
)
from apps.api.models import UserProfile, Rlc
from apps.api.serializers import (
    OldHasPermissionSerializer,
    UserProfileNameSerializer,
    GroupSerializer, HasPermissionNameSerializer, HasPermissionAllNamesSerializer,
)
from apps.recordmanagement.helpers import check_encryption_key_holders_and_grant
from apps.static.middleware import get_private_key_from_request


class HasPermissionViewSet(viewsets.ModelViewSet):
    queryset = HasPermission.objects.all()
    serializer_class = OldHasPermissionSerializer
    permission_classes = (IsAuthenticated,)

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
        if not HasPermission.objects.filter(**serializer.validated_data).exists():
            self.perform_create(serializer)

        permission = serializer.validated_data["permission"]
        if permission in get_record_encryption_keys_permissions():
            granting_users_private_key = self.request.user.get_private_key(request=request)
            check_encryption_key_holders_and_grant(request.user, granting_users_private_key)
        # check if permission in rec enc perms TODO: this would be more performant
        # get users private key
        # if rlc -> add rec enc for all rlc users
        # if group -> add for all group members
        # if user -> add for user

        has_permission = HasPermission.objects.get(**serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(HasPermissionAllNamesSerializer(instance=has_permission).data, status=status.HTTP_201_CREATED,
                        headers=headers)


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
