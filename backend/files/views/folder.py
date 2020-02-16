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

from backend.files.models import File, Folder, PermissionForFolder
from backend.files.serializers import FileSerializer, FolderSerializer
from backend.static.permissions import  PERMISSION_ACCESS_TO_FILES_RLC
from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT


class FolderViewSet(APIView):
    def get(self, request):
        path = 'files/' + request.query_params.get('path', '')
        folder = Folder.get_folder_from_path(path, request.user.rlc)

        children_rel = folder.child_folders.all()
        childs = list(children_rel)
        for child in childs:
            if not child.user_has_permission_read(request.user):
                children_rel = children_rel.exclude(name=child.name)
        data = FolderSerializer(children_rel, many=True).data

        files = File.objects.filter(folder=folder)
        files_data = FileSerializer(files, many=True).data
        obj = {
            'folders': data,
            'files': files_data
        }

        return Response(obj)


class DownloadFolderViewSet(APIView):
    def get(self, request):
        user = request.user
        if not user.has_permission(PERMISSION_ACCESS_TO_FILES_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        path = 'files/' + request.query_params.get('path', '')
        folder = Folder.get_folder_from_path(path, request.user.rlc)
        a = 10
        return Response({})
