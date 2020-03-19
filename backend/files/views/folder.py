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
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.files.models import File, Folder
from backend.files.serializers import FileSerializer, FolderSerializer
from backend.static.permissions import PERMISSION_ACCESS_TO_FILES_RLC
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT
from backend.static.storage_management import LocalStorageManager
from backend.static.storage_folders import get_temp_storage_path


class FolderBaseViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class FolderViewSet(APIView):
    def get(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_ACCESS_TO_FILES_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        path = 'files/' + request.query_params.get('path', '')
        folder = Folder.get_folder_from_path(path, request.user.rlc)
        if not folder:
            return Response({'folders': [], 'files': [], 'current_folder': None})

        # all_children = folder.child_folders.all()
        # children_list = list(all_children)
        # for child in children_list:
        #     if not child.user_has_permission_read(request.user):
        #         all_children = all_children.exclude(name=child.name)

        children_to_show = []
        for child in folder.child_folders.all().order_by('name'):
            if child.user_can_see_folder(user):
                children_to_show.append(child)
        return_obj = {'folders': FolderSerializer(children_to_show, many=True).data}

        if folder.user_has_permission_read(user):
            files = File.objects.filter(folder=folder)
            files_data = FileSerializer(files, many=True).data
            return_obj.update({'files': files_data})
        else:
            return_obj.update({'files': []})
        return_obj.update({'current_folder': FolderSerializer(folder).data})

        return Response(return_obj)


class DownloadFolderViewSet(APIView):
    def get(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_ACCESS_TO_FILES_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        path = 'files/' + request.query_params.get('path', '')
        folder = Folder.get_folder_from_path(path, request.user.rlc)
        folder.download_folder()
        path = get_temp_storage_path(folder.name)
        LocalStorageManager.zip_folder_and_delete(path, path)
        return LocalStorageManager.create_response_from_zip_file(path)
