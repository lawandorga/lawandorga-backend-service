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

import json

from rest_framework.response import Response
from rest_framework.views import APIView

from backend.files.models import File, Folder
from backend.static.multithreading import MultithreadedFileUploads
from backend.static.storage_management import LocalStorageManager


class UploadViewSet(APIView):
    def post(self, request):
        user = request.user
        files = request.FILES.getlist('files')
        file_information = LocalStorageManager.save_files_locally(files, json.loads(request.data['paths']))
        root_folder = Folder.get_folder_from_path('files/' + request.data['path'], user.rlc)

        s3_paths = []
        for file_info in file_information:
            # TODO: remove temp from local-file-paths at folder creation
            folder = Folder.create_folders_for_file_path(root_folder, file_info['local_file_path'][5:], user)
            new_file = File(name=file_info['file_name'], creator=user, size=file_info['file_size'], folder=folder,
                            last_editor=user)
            File.create_or_update(new_file)
            s3_paths.append(folder.get_file_key())

        filepaths = [n['local_file_path'] for n in file_information]
        MultithreadedFileUploads.encrypt_files_and_upload_to_s3(filepaths, s3_paths, 'aes_key')

        return Response({})
