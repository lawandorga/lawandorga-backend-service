from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class FilesStorage(S3Boto3Storage):
    bucket_name = settings.SCW_S3_BUCKET_NAME
