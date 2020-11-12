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
import shutil
import logging
from threading import Thread

from backend.api.models import Notification
from backend.files.models import File
from backend.static.encrypted_storage import EncryptedStorage
from backend.static.storage_management import LocalStorageManager
from backend.static.storage_folders import (
    get_temp_storage_path,
    combine_s3_folder_with_filename,
    get_filename_from_full_path,
    get_temp_storage_folder,
)


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
    def encrypt_files_and_upload_to_single_s3_folder(files, aes_key, s3_folder):
        """

        :param files: local filepaths
        :param aes_key: aes encryption key
        :param s3_folder: folder in s3 storage
        :return:
        """
        for local_file_path in files:
            EncryptedStorage.encrypt_file_and_upload_to_s3(
                local_file_path, aes_key, s3_folder
            )
            os.remove(local_file_path)

    @staticmethod
    @start_new_thread
    def encrypt_files_and_upload_to_s3(
        local_files: [str], s3_folders: [str], file_objects: [File], aes_key: str
    ):
        temp_folder = get_temp_storage_folder()

        for i in range(local_files.__len__()):
            (
                encrypted_filepath,
                encrypted_filename,
            ) = EncryptedStorage.encrypt_file_and_upload_to_s3(
                local_files[i], aes_key, s3_folders[i]
            )

            if not EncryptedStorage.file_exists_on_s3(
                encrypted_filename, s3_folders[i]
            ):
                EncryptedStorage.upload_file_to_s3(
                    encrypted_filepath,
                    combine_s3_folder_with_filename(s3_folders[i], encrypted_filename),
                )
                # check if download was successful now, if not, delete model
                if not EncryptedStorage.file_exists_on_s3(
                    encrypted_filename, s3_folders[i]
                ):
                    logger = logging.getLogger(__name__)
                    logger.info(
                        "second upload of file failed, deleting model: " + str()
                    )
                    Notification.objects.notify_file_upload_error(file_objects[i])
                    file_objects[i].delete()

        # if uploaded, delete local and check folders
        for file in local_files:
            os.remove(file)
            os.remove(file + ".enc")

        file_set: set = LocalStorageManager.get_all_files_in_folder(temp_folder)
        if file_set.__len__() == 0:  # TODO:  else?
            shutil.rmtree(temp_folder)
