from django.utils.crypto import get_random_string
from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Boto3Storage(S3Boto3Storage):
    def get_alternative_name(self, file_root, file_ext):
        """
        Return an alternative filename, by adding an underscore and a random 7
        character alphanumeric string (before the file name, if one
        exists) to the filename.
        """
        return "%s_%s%s" % (get_random_string(7), file_root, file_ext)
