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

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.api.models import Group
from backend.api.serializers import HasPermissionWithPermissionNameSerializer, HasPermissionSerializer
from backend.files.models import Folder, PermissionForFolder, FolderPermission
from backend.files.serializers import PermissionForFolderSerializer, PermissionForFolderNestedSerializer
from backend.static.error_codes import ERROR__API__ID_NOT_FOUND, ERROR__API__PERMISSION__INSUFFICIENT, \
    ERROR__API__WRONG_RLC, ERROR__API__MISSING_ARGUMENT, ERROR__API__ID_NOT_FOUND
from backend.static.permissions import PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
from backend.files.static.folder_permissions import PERMISSION_READ_FOLDER, PERMISSION_WRITE_FOLDER


class PermissionForFolderViewSet(viewsets.ModelViewSet):
    queryset = PermissionForFolder.objects.all()
    serializer_class = PermissionForFolderSerializer

    def create(self, request):
        user = request.user
        if not user.is_superuser and not user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)
        if 'group' not in request.data or 'folder' not in request.data or 'permission' not in request.data:
            raise CustomError(ERROR__API__MISSING_ARGUMENT)

        try:
            group = Group.objects.get(pk=request.data['group'])
            folder = Folder.objects.get(pk=request.data['folder'])

            if request.data['permission'] == 'read':
                permission = FolderPermission.objects.get(name=PERMISSION_READ_FOLDER)
            elif request.data['permission'] == 'write':
                permission = FolderPermission.objects.get(name=PERMISSION_WRITE_FOLDER)
        except:
            raise CustomError(ERROR__API__ID_NOT_FOUND)

        permission_to_create = PermissionForFolder(permission=permission, folder=folder, group_has_permission=group)
        permission_to_create.save()
        return Response({'success': True})

    def destroy(self, request, *args, **kwargs):
        if 'pk' not in kwargs:
            raise CustomError(ERROR__API__MISSING_ARGUMENT)
        user = request.user

        a = list(PermissionForFolder.objects.all())
        try:
            permission_for_folder = PermissionForFolder.objects.get(pk=kwargs['pk'])
        except:
            raise CustomError(ERROR__API__ID_NOT_FOUND)
        if not user.is_superuser and not user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC, for_rlc=permission_for_folder.folder.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)
        permission_for_folder.delete()
        return Response({'success': True})


class PermissionForFolderPerFolderViewSet(APIView):
    def get(self, request, id):
        user = request.user

        if not user.is_superuser and not user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC,
                                                             for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        try:
            folder = Folder.objects.get(pk=id)
        except:
            raise CustomError(ERROR__API__ID_NOT_FOUND)
        if folder.rlc != user.rlc:
            raise CustomError(ERROR__API__WRONG_RLC)

        folder_permissions, folder_visible, general_permissions = folder.get_all_groups_permissions_new()
        return_object = {
            'folder_permissions': PermissionForFolderNestedSerializer(folder_permissions, many=True).data,
            'folder_visible': PermissionForFolderNestedSerializer(folder_visible, many=True).data,
            'general_permissions': HasPermissionSerializer(general_permissions, many=True).data
        }

        return Response(return_object)

