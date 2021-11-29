from apps.static.storage_folders import clean_filename, clean_string
from rest_framework.exceptions import ParseError
from django.core.files.storage import default_storage
from apps.static.encryption import AESEncryption
from apps.static.logger import Logger
from apps.api.errors import CustomError
from botocore.client import BaseClient
from apps.static import error_codes
from django.conf import settings
import boto3
import os


class EncryptedStorage:
    @staticmethod
    def get_s3_client():
        return boto3.session.Session().client(
            service_name="s3",
            region_name="fr-par",
            endpoint_url="https://s3.fr-par.scw.cloud",
            aws_access_key_id=settings.SCW_ACCESS_KEY,
            aws_secret_access_key=settings.SCW_SECRET_KEY,
        )

    @staticmethod
    def upload_to_s3(local_filepath, filename):
        EncryptedStorage.get_s3_client().upload_file(local_filepath, settings.SCW_S3_BUCKET_NAME, filename)

    @staticmethod
    def encrypt_file_and_upload_to_s3(local_filepath, aes_key, key):
        encrypted_file = AESEncryption.encrypt_file(local_filepath, aes_key)
        encrypted_key = '{}.enc'.format(key)
        EncryptedStorage.get_s3_client().upload_file(encrypted_file, settings.SCW_S3_BUCKET_NAME, encrypted_key)

    @staticmethod
    def file_exists(key):
        response = EncryptedStorage.get_s3_client().list_objects_v2(
            Bucket=settings.SCW_S3_BUCKET_NAME,
            Prefix=key,
        )
        for obj in response.get('Contents', []):
            if obj['Key'] == key:
                return True
        return False

    @staticmethod
    def download_file_from_s3(s3_key, filename=None):
        if not filename:
            filename = s3_key[s3_key.rindex("/") + 1:]
        s3: BaseClient = EncryptedStorage.get_s3_client()

        try:
            filename = clean_string(filename)
            os.makedirs(filename[: filename.rindex("/") + 1])
        except:
            pass
        try:
            s3.download_file(settings.SCW_S3_BUCKET_NAME, s3_key, filename)
        except Exception as e:
            raise CustomError(error_codes.ERROR__API__DOWNLOAD__NO_SUCH_KEY)

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
            downloaded_file_name = clean_string(downloaded_file_name)
        # TODO: what happens to local_Folder if downloaded file name is given???
        EncryptedStorage.download_file_from_s3(s3_key, downloaded_file_name)
        AESEncryption.decrypt_file(downloaded_file_name, encryption_key)
        os.remove(downloaded_file_name)

    @staticmethod
    def delete_on_s3(s3_key):
        try:
            EncryptedStorage.get_s3_client().delete_object(Bucket=settings.SCW_S3_BUCKET_NAME, Key=s3_key)
        except Exception as e:
            Logger.error("couldnt delete file from s3: " + s3_key)
            # raise CustomError(error_codes.ERROR__API__STORAGE__DELETE__NO_SUCH_KEY)

    @staticmethod
    def download_encrypted_file(file_key, aes_key):
        # open the file
        try:
            file = default_storage.open(file_key)
        except FileNotFoundError:
            raise ParseError('The file was not found.')
        # decrypt the file
        file = AESEncryption.decrypt_bytes_file(file, aes_key)
        file.seek(0)
        # return
        return file
