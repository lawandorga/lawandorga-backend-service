from rest_framework.exceptions import ParseError
from django.core.files.storage import default_storage
from apps.static.encryption import AESEncryption


class EncryptedStorage:
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
