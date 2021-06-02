#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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

from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.api.serializers import OldHasPermissionSerializer
from backend.files.models.folder import Folder
from backend.files.models.permission_for_folder import PermissionForFolder
from backend.files.serializers import (
    PermissionForFolderSerializer,
    PermissionForFolderNestedSerializer,
)
from backend.static.error_codes import (
    ERROR__API__PERMISSION__INSUFFICIENT,
    ERROR__API__WRONG_RLC,
    ERROR__API__ID_NOT_FOUND,
)
from backend.static.permissions import PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC


class PermissionForFolderViewSet(viewsets.ModelViewSet):
    queryset = PermissionForFolder.objects.all()
    serializer_class = PermissionForFolderSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC):
            raise PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(PermissionForFolderNestedSerializer(instance=instance).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC):
            raise PermissionDenied()

        return super().destroy(request, *args, **kwargs)


class PermissionForFolderPerFolderViewSet(APIView):
    def get(self, request, id):
        user = request.user

        if not user.is_superuser and not user.has_permission(
            PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC, for_rlc=user.rlc
        ):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        try:
            folder = Folder.objects.get(pk=id)
        except:
            raise CustomError(ERROR__API__ID_NOT_FOUND)
        if folder.rlc != user.rlc:
            raise CustomError(ERROR__API__WRONG_RLC)

        (
            folder_permissions,
            folder_visible,
            general_permissions,
        ) = folder.get_all_groups_permissions()
        return_object = {
            "folder_permissions": PermissionForFolderNestedSerializer(
                folder_permissions, many=True
            ).data,
            "folder_visible": PermissionForFolderNestedSerializer(
                folder_visible, many=True
            ).data,
            "general_permissions": OldHasPermissionSerializer(
                general_permissions, many=True
            ).data,
        }

        return Response(return_object)
