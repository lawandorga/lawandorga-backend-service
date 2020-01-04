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
import zipfile
import base64
import boto3
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.response import Response
from storages.backends.s3boto3 import S3Boto3Storage
from botocore.client import Config
from backend.static.encryption import AESEncryption


class EncryptedStorage:
    @staticmethod
    def upload_file_to_s3(filename, key):
        """

        :param filename: file which should get uploaded
        :param bucket: the bucket to upload to
        :param key: the key of the uploaded file
        :return: -
        """
        s3_bucket = settings.AWS_S3_BUCKET_NAME
        session = boto3.session.Session(region_name=settings.AWS_S3_REGION_NAME)
        s3 = session.client('s3', config=Config(signature_version='s3v4'))
        s3.upload_file(filename, s3_bucket, key)

    @staticmethod
    def encrypt_file_and_upload_to_s3(file, key, s3_folder):
        AESEncryption.encrypt_file_wo_iv(file, key)
        file = file + '.enc'  # encryption appends '.enc'
        s3_filename = s3_folder + file[file.rindex('/'):]
        EncryptedStorage.upload_file_to_s3(file, s3_filename)

    @staticmethod
    def download_file_from_s3(s3_key, filename=None):
        if not filename:
            pass # TODO
        s3_bucket = settings.AWS_S3_BUCKET_NAME
        session = boto3.session.Session(region_name=settings.AWS_S3_REGION_NAME)
        s3 = session.client('s3', config=Config(signature_version='s3v4'))
        s3.download_file(s3_bucket, s3_key, filename)

    @staticmethod
    def download_from_s3_and_decrypt_file(s3_key, key, local_folder, downloaded_file_name=None):
        if not downloaded_file_name:
            filename = s3_key[s3_key.rindex('/') + 1:]
            downloaded_file_name = os.path.join(local_folder, filename)
        EncryptedStorage.download_file_from_s3(s3_key, downloaded_file_name)
        AESEncryption.decrypt_file_wo_iv(downloaded_file_name, key)
