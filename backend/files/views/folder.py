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
from backend.files.models import File, Folder
from backend.files.serializers import FileSerializer, FolderSerializer
from backend.static.error_codes import (
    ERROR__API__ID_NOT_FOUND,
    ERROR__API__MISSING_ARGUMENT,
    ERROR__API__PERMISSION__INSUFFICIENT,
    ERROR__FILES__FOLDER_NOT_EXISTING,
)
from backend.static.permissions import PERMISSION_ACCESS_TO_FILES_RLC
from backend.static.storage_folders import get_temp_storage_path
from backend.static.storage_management import LocalStorageManager


class FolderBaseViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class FolderViewSet(APIView):
    def get(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_ACCESS_TO_FILES_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        path = "files/" + request.query_params.get("path", "")
        if path.endswith("//"):
            path = path[:-2]
        folder = Folder.get_folder_from_path(path, request.user.rlc)
        if not folder:
            raise CustomError(ERROR__FILES__FOLDER_NOT_EXISTING)
            # return Response({'folders': [], 'files': [], 'current_folder': None})

        children_to_show = []

        for child in folder.child_folders.all().order_by("name"):
            if child.user_can_see_folder(user):
                children_to_show.append(child)
        return_obj = {"folders": FolderSerializer(children_to_show, many=True).data}

        if folder.user_has_permission_read(user):
            files = File.objects.filter(folder=folder)
            files_data = FileSerializer(files, many=True).data
            return_obj.update({"files": files_data})
        else:
            return_obj.update({"files": []})
        return_obj.update({"current_folder": FolderSerializer(folder).data})

        return_obj.update({"write_permission": folder.user_has_permission_write(user)})
        return Response(return_obj)

    def post(self, request):
        user = request.user
        data = request.data
        if "name" not in data or "parent_folder_id" not in data:
            raise CustomError(ERROR__API__MISSING_ARGUMENT)
        try:
            parent_folder = Folder.objects.get(pk=data["parent_folder_id"])
        except:
            raise CustomError(ERROR__API__ID_NOT_FOUND)
        if (
            parent_folder.rlc != user.rlc
            and not user.is_superuser
            and not parent_folder.user_has_permission_write(user)
        ):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        folder = Folder(
            name=data["name"], creator=user, parent=parent_folder, rlc=user.rlc
        )
        folder.save()

        return Response(FolderSerializer(folder).data)


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
