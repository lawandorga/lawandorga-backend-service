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

import os
from threading import Thread

from backend.static.encrypted_storage import EncryptedStorage
from backend.static.storage_folders import get_temp_storage_path, combine_s3_folder_with_filename, get_filename_from_full_path


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


class MultithreadedFileUploads:
    @staticmethod
    @start_new_thread
    def encrypt_file_and_upload_to_s3(filename, key, s3_folder):
        EncryptedStorage.encrypt_file_and_upload_to_s3(filename, key, s3_folder)
        os.remove(filename)


    @staticmethod
    @start_new_thread
    def encrypt_files_and_upload_to_s3(files, aes_key, s3_folder):
        """

        :param files: local filepaths
        :param aes_key: aes encryption key
        :param s3_folder: folder in s3 storage
        :return:
        """
        for local_file_path in files:
            EncryptedStorage.encrypt_file_and_upload_to_s3(local_file_path, aes_key, s3_folder)
            os.remove(local_file_path)
