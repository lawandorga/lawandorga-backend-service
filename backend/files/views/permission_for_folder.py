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
from backend.api.errors import CustomError
from backend.api.models import Group
from backend.files.models import Folder, PermissionForFolder
from backend.files.serializers import PermissionForFolderSerializer
from backend.static.permissions import PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC
from backend.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT, ERROR__API__ID_NOT_FOUND, ERROR__API__WRONG_RLC


class PermissionForFolderViewSet(viewsets.ModelViewSet):
    queryset = PermissionForFolder.objects.all()
    serializer_class = PermissionForFolderSerializer


class PermissionForFolderPerFolderViewSet(APIView):
    def get(self, request, id):
        user = request.user

        if not user.has_permission(PERMISSION_MANAGE_FOLDER_PERMISSIONS_RLC, for_rlc=user.rlc):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)

        try:
            folder = Folder.objects.get(pk=id)
        except:
            raise CustomError(ERROR__API__ID_NOT_FOUND)
        if folder.rlc != user.rlc:
            raise CustomError(ERROR__API__WRONG_RLC)

        # get all groups? for each group permission?
        groups = list(Group.objects.filter(from_rlc=user.rlc))
        visible = []
        read = []
        write = []
        for group in groups:
            pass

        return Response({})
