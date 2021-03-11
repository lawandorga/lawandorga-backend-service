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

from threading import Thread
from backend.api.models import Notification
from backend.files.models import File
from backend.static.encrypted_storage import EncryptedStorage
from backend.static.storage_management import LocalStorageManager
from backend.static.storage_folders import (
    combine_s3_folder_with_filename,
    get_temp_storage_folder,
)
from backend.static.logger import Logger


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


class MultithreadedFileUploads:
    # @staticmethod
    # @start_new_thread
    # def encrypt_file_and_upload_to_s3(
    #     local_file_path: str, key: str, s3_folder: str
    # ) -> None:
    #     EncryptedStorage.encrypt_file_and_upload_to_s3(local_file_path, key, s3_folder)
    #     LocalStorageManager.delete_file(local_file_path)

    @staticmethod
    @start_new_thread
    def encrypt_files_and_upload_to_single_s3_folder(
        files: [str], s3_folder: str, aes_key: str
    ) -> None:
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
            LocalStorageManager.delete_file_and_enc(local_file_path)
            LocalStorageManager.delete_folder_if_empty(get_temp_storage_folder())

    @staticmethod
    @start_new_thread
    def encrypt_files_and_upload_to_s3(
        local_files: [str], s3_folders: [str], file_objects: [File], aes_key: str
    ):
        for i in range(local_files.__len__()):
            (
                encrypted_filepath,
                encrypted_filename,
            ) = EncryptedStorage.encrypt_file_and_upload_to_s3(
                local_files[i], aes_key, s3_folders[i]
            )
            if not file_objects[i].exists_on_s3():
                EncryptedStorage.upload_file_to_s3(
                    encrypted_filepath,
                    combine_s3_folder_with_filename(s3_folders[i], encrypted_filename),
                )
                # check if download was successful now, if not, delete model
                if not file_objects[i].exists_on_s3():
                    Logger.error(
                        "second upload of file failed, deleting model: "
                        + file_objects[i].name
                    )
                    Notification.objects.notify_file_upload_error(file_objects[i])
                    file_objects[i].delete()

        # if uploaded, delete local and check folders
        for file in local_files:
            LocalStorageManager.delete_file_and_enc(file)

        LocalStorageManager.delete_folder_if_empty(get_temp_storage_folder())
        # TODO: get if not successful?
