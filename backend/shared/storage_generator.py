#  rlcapp - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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

from backend.static.error_codes import *
from backend.api.errors import CustomError


def generate_presigned_post(file_name, file_type, file_dir=''):
    """
    generates a presigned post for a given file so you can upload it directly
    :param file_name: string, the file name
    :param file_type: string, the type of the file
    :param file_dir: string, the directory where the file should be
    :return:
    """
    if file_name == '':
        raise CustomError(ERROR__RECORD__UPLOAD__NO_FILE_NAME)
    if file_type == '':
        raise CustomError(ERROR__RECORD__UPLOAD__NO_FILE_TYPE)

    s3_bucket = settings.AWS_S3_BUCKET_NAME

    if file_dir != '' and not file_dir.endswith('/'):
        file_dir = file_dir + "/"

    session = boto3.session.Session(region_name=settings.AWS_S3_REGION_NAME)
    s3 = session.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    presigned_post = s3.generate_presigned_post(
        Bucket=s3_bucket,
        Key=file_dir + file_name,
        Fields={"acl": "private", "Content-Type": file_type},
        ExpiresIn=3600
    )
    return {
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (s3_bucket, file_name)
    }


def generate_presigned_url(filekey):
    """
    generates a presigned url, with this you can download the specified file of filekey
    :param filekey: string, combination of dir and name of the file (absolute path)
    :return:
    """
    s3_bucket = settings.AWS_S3_BUCKET_NAME
    if filekey == '':
        raise CustomError(ERROR__API__DOWNLOAD__NO_FILE_SPECIFIED)

    session = boto3.session.Session(region_name=settings.AWS_S3_REGION_NAME)
    s3 = session.client('s3', config=Config(signature_version='s3v4'))
    try:
        s3.get_object(Bucket=s3_bucket, Key=filekey)
    except Exception as ex:
        raise CustomError(ERROR__API__DOWNLOAD__NO_SUCH_KEY)

    presigned_url = s3.generate_presigned_url(ClientMethod='get_object',
                                              Params={'Bucket': s3_bucket, 'Key': filekey},
                                              ExpiresIn=100)
    return {
        'data': presigned_url
    }


def check_file_and_get_information(file_dir, filekey):
    s3_bucket = settings.AWS_S3_BUCKET_NAME
    if filekey == '':
        raise CustomError(ERROR__API__DOWNLOAD__NO_FILE_SPECIFIED)
    if not file_dir.endswith('/'):
        file_dir = file_dir + "/"

    session = boto3.session.Session(region_name=settings.AWS_S3_REGION_NAME)
    s3 = session.client('s3', config=Config(signature_version='s3v4'))

    try:
        objects = s3.list_objects_v2(Bucket=s3_bucket, Prefix=file_dir)
    except Exception as ex:
        raise CustomError(ERROR__API__STORAGE__DIR_NOT_FOUND)

    if 'Contents' not in objects:
        raise CustomError(ERROR__API__STORAGE__DIR_EMPTY)

    for object in objects['Contents']:
        if object['Key'] == file_dir+filekey:
            return {
                "size": object['Size'],
                "key": object['Key']
            }
    raise CustomError(ERROR__API__STORAGE__CHECK_FILE_NOT_FOUND)


def download_file(source_file, dest_file):
    s3_bucket = settings.AWS_S3_BUCKET_NAME
    session = boto3.session.Session(region_name=settings.AWS_S3_REGION_NAME)
    s3 = session.client('s3', config=Config(signature_version='s3v4'))
    s3.download_file(s3_bucket, source_file, dest_file)


def zip_files_and_create_response(file_names, zip_file_name):
    """
    bundles all files in file_names to zip and creates response
    deletes files and zip afterwards
    :param file_names: list of filenames which should be included in the zip file
    :param zip_file_name: name of the zip file
    :return:
    """
    zip_file = zipfile.ZipFile(zip_file_name, "w")
    for file in file_names:
        zip_file.write(file)
    zip_file.close()
    for file in file_names:
        os.remove(file)
    encoded_file = base64.b64encode(open(zip_file_name, 'rb').read())
    res = Response(encoded_file, content_type='application/zip')
    res['Content-Disposition'] = 'attachment; filename="' + zip_file_name + '"'
    os.remove(zip_file_name)
    return res


class CachedS3Boto3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super(CachedS3Boto3Storage, self).__init__(*args, **kwargs)
        self.local_storage = default_storage(
            "compressor.storage.GzipCompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3Boto3Storage, self).save(name, content)
        self.local_storage._save(name, content)
        return name
