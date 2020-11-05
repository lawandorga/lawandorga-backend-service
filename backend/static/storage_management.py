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

import shutil
import base64
import os
from rest_framework.response import Response

from backend.static.storage_folders import (
    get_temp_storage_path,
    get_temp_storage_folder,
)


class LocalStorageManager:
    @staticmethod
    def save_files_locally(files, paths=None):
        """
        saves files in temp local storage and returns filepaths and file_names
        :param files: InMemoryObjects
        :param paths:
        :return:
        """
        # local_file_paths = []
        # file_names = []
        # file_sizes = []
        output_file_information = []
        for file_information in files:
            if paths is None:
                local_file_path = get_temp_storage_path(file_information.name)
            else:
                as_path = file_information.name + ";" + str(file_information.size)
                for path in paths:
                    if path.endswith(as_path):
                        real_path_part = path[
                            : -(1 + str(file_information.size).__len__())
                        ]
                        if path.startswith("/"):
                            real_path_part = real_path_part[1:]
                        local_file_path = os.path.join(
                            get_temp_storage_path(real_path_part)
                        )
                        break
            try:
                os.makedirs(os.path.dirname(local_file_path))
            except:
                pass
            file = open(local_file_path, "wb")
            if file_information.multiple_chunks():
                for chunk in file_information.chunks():
                    file.write(chunk)
            else:
                file.write(file_information.read())
                file.close()
            # local_file_paths.append(local_file_path)
            # file_names.append(file_information.name)
            # file_sizes.append(file_information.size)
            output_file_information.append(
                {
                    "file_name": file_information.name,
                    "file_size": file_information.size,
                    "local_file_path": local_file_path,
                }
            )
        return output_file_information

    @staticmethod
    def zip_folder_and_delete(zip_path, folder_path):
        shutil.make_archive(zip_path, "zip", folder_path)
        shutil.rmtree(folder_path)

    @staticmethod
    def create_response_from_zip_file(zip_path: str):
        encoded_file = base64.b64encode(open(zip_path, "rb").read())
        res = Response(encoded_file, content_type="application/zip")
        res["Content-Disposition"] = (
            'attachment; filename="'
            + zip_path.encode("ascii", "ignore").decode("ascii")
            + '"'
        )
        os.remove(zip_path)
        return res
