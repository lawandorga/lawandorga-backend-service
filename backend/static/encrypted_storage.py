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
from django.conf import settings
import logging

from backend.api.errors import CustomError
from backend.static import error_codes
from backend.static.encryption import AESEncryption
from backend.static.storage_folders import combine_s3_folder_with_filename


class EncryptedStorage:
    @staticmethod
    def upload_file_to_s3(filename, key):
        """

        :param filename: file which should get uploaded
        :param key: the key of the uploaded file
        :return: -
        """
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3",
            region_name="fr-par",
            use_ssl=True,
            endpoint_url="http://s3.fr-par.scw.cloud",
            aws_access_key_id=settings.SCW_ACCESS_KEY,
            aws_secret_access_key=settings.SCW_SECRET_KEY,
        )
        s3_bucket = settings.SCW_S3_BUCKET_NAME
        s3.upload_file(filename, s3_bucket, key)

    @staticmethod
    def encrypt_file_and_upload_to_s3(filepath, aes_key, s3_folder):
        encrypted_filepath, encrypted_filename = AESEncryption.encrypt_file(
            filepath, aes_key
        )
        EncryptedStorage.upload_file_to_s3(
            encrypted_filepath,
            combine_s3_folder_with_filename(s3_folder, encrypted_filename),
        )
        os.remove(encrypted_filepath)

    @staticmethod
    def download_file_from_s3(s3_key, filename=None):
        if not filename:
            filename = s3_key[s3_key.rindex("/") + 1 :]
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3",
            region_name="fr-par",
            use_ssl=True,
            endpoint_url="http://s3.fr-par.scw.cloud",
            aws_access_key_id=settings.SCW_ACCESS_KEY,
            aws_secret_access_key=settings.SCW_SECRET_KEY,
        )
        s3_bucket = settings.SCW_S3_BUCKET_NAME

        import os

        try:
            os.makedirs(filename[: filename.rindex("/") + 1])
        except:
            pass
        try:
            s3.download_file(s3_bucket, s3_key, filename)
        except Exception as e:
            raise CustomError(error_codes.ERROR__API__DOWNLOAD__NO_SUCH_KEY)

    @staticmethod
    def download_from_s3_and_decrypt_file(
        s3_key, encryption_key, local_folder, downloaded_file_name=None
    ):
        if not downloaded_file_name:
            filename = s3_key[s3_key.rindex("/") + 1 :]
            downloaded_file_name = os.path.join(local_folder, filename)
        # TODO: what happens to local_Folder if downloaded file name is given???
        EncryptedStorage.download_file_from_s3(s3_key, downloaded_file_name)
        AESEncryption.decrypt_file(downloaded_file_name, encryption_key)
        os.remove(downloaded_file_name)

    @staticmethod
    def delete_on_s3(s3_key):
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3",
            region_name="fr-par",
            use_ssl=True,
            endpoint_url="http://s3.fr-par.scw.cloud",
            aws_access_key_id=settings.SCW_ACCESS_KEY,
            aws_secret_access_key=settings.SCW_SECRET_KEY,
        )
        s3_bucket = settings.SCW_S3_BUCKET_NAME
        try:
            s3.delete_object(Bucket=s3_bucket, Key=s3_key)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error("couldnt delete file from s3: " + s3_key)
            # raise CustomError(error_codes.ERROR__API__STORAGE__DELETE__NO_SUCH_KEY)
