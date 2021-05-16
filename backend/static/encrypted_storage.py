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
import boto3
from botocore.client import BaseClient
from django.conf import settings

from backend.api.errors import CustomError
from backend.static import error_codes
from backend.static.encryption import AESEncryption
from backend.static.storage_folders import combine_s3_folder_with_filename, clean_filename
from backend.static.logger import Logger
import logging

logger = logging.getLogger(__name__)


class EncryptedStorage:
    @staticmethod
    def get_s3_client() -> BaseClient:
        session = boto3.session.Session()
        return session.client(
            service_name="s3",
            region_name="fr-par",
            endpoint_url="https://s3.fr-par.scw.cloud",
            aws_access_key_id=settings.SCW_ACCESS_KEY,
            aws_secret_access_key=settings.SCW_SECRET_KEY,
        )

    @staticmethod
    def upload_file_to_s3(filename, key):
        """

        :param filename: file which should get uploaded
        :param key: the key of the uploaded file
        :return: -
        """
        s3: BaseClient = EncryptedStorage.get_s3_client()
        s3.upload_file(filename, settings.SCW_S3_BUCKET_NAME, key)

    @staticmethod
    def encrypt_file_and_upload_to_s3(
        local_filepath: str, aes_key: str, s3_folder: str
    ) -> (str, str):
        """
        encrypts file on local filesystem and uploads it to s3
        :param local_filepath: local filepath
        :param aes_key: encryption key for encrypting the file
        :param s3_folder: s3 folder to upload to
        :return: encrypted filepath and encrypted filename
        """

        encrypted_filepath, encrypted_filename = AESEncryption.encrypt_file(
            local_filepath, aes_key
        )
        Logger.debug("file encrypted: " + str(local_filepath))

        EncryptedStorage.upload_file_to_s3(
            encrypted_filepath,
            combine_s3_folder_with_filename(s3_folder, encrypted_filename),
        )
        Logger.debug("file uploaded to: " + str(s3_folder) + str(encrypted_filename))
        Logger.info("file encrypted and uploaded to s3: " + local_filepath)
        return encrypted_filepath, encrypted_filename

    @staticmethod
    def file_exists(s3_key: str) -> bool:
        try:
            s3: BaseClient = EncryptedStorage.get_s3_client()
            s3.get_object(
                Bucket=settings.SCW_S3_BUCKET_NAME, Key=s3_key,
            )
        except Exception as e:
            Logger.info("file does not exist on s3: " + s3_key)
            return False
        return True

    @staticmethod
    def download_file_from_s3(s3_key, filename=None):
        if not filename:
            filename = s3_key[s3_key.rindex("/") + 1 :]
        s3: BaseClient = EncryptedStorage.get_s3_client()

        try:
            os.makedirs(filename[: filename.rindex("/") + 1])
        except:
            pass
        # try:
        logger.error('s3key: {}, filename: {}'.format(s3_key, filename))
        s3.download_file(settings.SCW_S3_BUCKET_NAME, s3_key, clean_filename(filename))
        # except Exception as e:

            # raise CustomError(error_codes.ERROR__API__DOWNLOAD__NO_SUCH_KEY)

    @staticmethod
    def download_from_s3_and_decrypt_file(
        s3_key, encryption_key, local_folder, downloaded_file_name=None
    ):
        """
        downloads file from s3,
        :param s3_key:
        :param encryption_key:
        :param local_folder:
        :param downloaded_file_name:
        :return:
        """
        s3_key = clean_filename(s3_key)
        if not downloaded_file_name:
            filename = s3_key[s3_key.rindex("/") + 1:]
            downloaded_file_name = os.path.join(local_folder, filename)
        # TODO: what happens to local_Folder if downloaded file name is given???
        EncryptedStorage.download_file_from_s3(s3_key, downloaded_file_name)
        AESEncryption.decrypt_file(downloaded_file_name, encryption_key)
        os.remove(downloaded_file_name)

    @staticmethod
    def delete_on_s3(s3_key):
        s3: BaseClient = EncryptedStorage.get_s3_client()
        try:
            s3.delete_object(Bucket=settings.SCW_S3_BUCKET_NAME, Key=s3_key)
        except Exception as e:
            Logger.error("couldnt delete file from s3: " + s3_key)
            # raise CustomError(error_codes.ERROR__API__STORAGE__DELETE__NO_SUCH_KEY)
