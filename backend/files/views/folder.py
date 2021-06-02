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
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.api.errors import CustomError
from backend.api.models import Group
from backend.files.models import PermissionForFolder
from backend.files.models.file import File
from backend.files.models.folder import Folder
from backend.files.serializers import FileSerializer, FolderSerializer, FolderCreateSerializer, FolderPathSerializer, \
    PermissionForFolderNestedSerializer
from backend.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT
from backend.static.permissions import PERMISSION_ACCESS_TO_FILES_RLC, PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
from backend.static.storage_folders import get_temp_storage_path
from backend.static.storage_management import LocalStorageManager


class FolderBaseViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.none()
    serializer_class = FolderSerializer

    def get_queryset(self):
        return Folder.objects.filter(rlc=self.request.user.rlc)

    def get_serializer_class(self):
        if self.action in ['create']:
            return FolderCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return FolderPathSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        instance = Folder.objects.get(parent=None, rlc=request.user.rlc)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True)
    def items(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        folders = []
        for folder in instance.child_folders.all():
            if folder.user_can_see_folder(user):
                folders.append(folder)
        folder_data = FolderSerializer(folders, many=True).data

        files_data = []
        if instance.user_has_permission_read(user) or instance.user_has_permission_write(user):
            files = File.objects.filter(folder=instance)
            files_data = FileSerializer(files, many=True).data

        data = folder_data + files_data
        return Response(data)

    @action(detail=True)
    def permissions(self, request, *args, **kwargs):
        if not request.user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC):
            raise PermissionDenied()

        folder = self.get_object()

        groups = Group.objects.filter(from_rlc=request.user.rlc)

        parents = folder.get_all_parents()
        children = folder.get_all_children()

        from_above = PermissionForFolder.objects.filter(
            folder__in=parents, group_has_permission__in=groups
        )

        normal = PermissionForFolder.objects.filter(
            folder=folder, group_has_permission__in=groups
        )

        from_below = PermissionForFolder.objects.filter(
            folder__in=children, group_has_permission__in=groups
        )

        permissions = []
        permissions += PermissionForFolderNestedSerializer(from_above, from_direction='ABOVE', many=True).data
        permissions += PermissionForFolderNestedSerializer(normal, many=True).data
        permissions += PermissionForFolderNestedSerializer(from_below, from_direction='BELOW', many=True).data

        return Response(permissions)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['parent'].user_has_permission_write(request.user):
            raise PermissionDenied()

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.child_folders.exists() or instance.files_in_folder.exists():
            data = {
                'detail': 'There are still items in this folder. It can not be deleted.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not instance.user_has_permission_write(request.user):
            raise PermissionDenied()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadFolderViewSet(APIView):
    def get(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_ACCESS_TO_FILES_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        path = "files/" + request.query_params.get("path", "")
        folder = Folder.get_folder_from_path(path, request.user.rlc)
        folder.download_folder()
        path = get_temp_storage_path(folder.name)
        LocalStorageManager.zip_folder_and_delete(path, path)
        return LocalStorageManager.create_response_from_zip_file(path)
