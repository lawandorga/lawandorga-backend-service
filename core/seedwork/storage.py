from django.core.files.storage import default_storage

from core.seedwork.encryption import AESEncryption


def encrypt_and_upload_file(file, key, aes_key):
    file = AESEncryption.encrypt_in_memory_file(file, aes_key)
    file = default_storage.save(key, file)
    return file


def download_and_decrypt_file(file_key, aes_key):
    file = default_storage.open(file_key)
    file = AESEncryption.decrypt_bytes_file(file, aes_key)
    file.seek(0)
    return file
