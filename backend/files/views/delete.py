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

from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.errors import CustomError
from backend.files.models.file import File
from backend.files.models.folder import Folder
from backend.static.error_codes import ERROR__API__PERMISSION__INSUFFICIENT


class DeleteViewSet(APIView):
    def post(self, request):
        user = request.user
        root_folder = Folder.get_folder_from_path(
            "files/" + request.data["path"], user.rlc
        )
        if not root_folder.user_has_permission_write(user):
            raise CustomError(ERROR__API__PERMISSION__INSUFFICIENT)
        entries = request.data["entries"]
        for entry in entries:
            if entry["type"] == 1:
                # file
                file = File.objects.get(pk=entry["id"])
                file.delete()
            else:
                folder = Folder.objects.get(pk=entry["id"])
                folder.delete()
        return Response({"success": True})
