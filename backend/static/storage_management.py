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

from backend.static.storage_folders import get_temp_storage_path


class LocalStorageManager:
    @staticmethod
    def save_files_locally(files):
        """
        saves files in temp local storage and returns filepaths and file_names
        :param files: InMemoryObjects
        :return:
        """
        local_file_paths = []
        file_names = []
        file_sizes = []
        output_file_information = []
        for file_information in files:
            local_file_path = get_temp_storage_path(file_information.name)
            file = open(local_file_path, 'wb')
            if file_information.multiple_chunks():
                for chunk in file_information.chunks():
                    file.write(chunk)
            else:
                file.write(file_information.read())
                file.close()
            local_file_paths.append(local_file_path)
            file_names.append(file_information.name)
            file_sizes.append(file_information.size)
            output_file_information.append({
                'file_name': file_information.name,
                'file_size': file_information.size,
                'local_file_path': local_file_path
            })
        return output_file_information
