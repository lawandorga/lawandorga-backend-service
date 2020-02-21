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

from backend.files.models import Folder, File
from backend.static.storage_folders import get_temp_storage_folder
from backend.static.storage_management import LocalStorageManager


class DownloadViewSet(APIView):
    def post(self, request):
        entries = request.data['entries']
        request_path = request.data['path']
        if request_path == '':
            request_path = 'root'

        root_folder_name = get_temp_storage_folder() + '/' + request_path
        for entry in entries:
            if entry['type'] == 1:
                # file
                file = File.objects.get(pk=entry['id'])
                file.download(root_folder_name)
            else:
                folder = Folder.objects.get(pk=entry['id'])
                folder.download_folder(root_folder_name)

        LocalStorageManager.zip_folder_and_delete(root_folder_name, root_folder_name)
        return LocalStorageManager.create_response_from_zip_file(get_temp_storage_folder() + '/' + request_path + '.zip')
