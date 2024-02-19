import os
import secrets
import string
from hashlib import sha3_256

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from core.folders.domain.value_objects.encryption import (
    EncryptionDecryptionError,
    SymmetricEncryption,
)


class SymmetricEncryptionV1(SymmetricEncryption):
    VERSION = "S1"

    def __init__(self, key: str):
        assert isinstance(key, str)

        self.__key = key
        super().__init__()

    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        password_characters = string.ascii_letters + string.digits + string.punctuation
        return (
            "".join(secrets.choice(password_characters) for _ in range(64)),
            cls.VERSION,
        )

    def encrypt(self, data: bytes) -> bytes:
        assert self.__key is not None

        iv = os.urandom(16)
        bytes_key = bytes(self.__key, "utf-8")
        hashed_key_bytes = sha3_256(bytes_key).digest()
        cipher = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)
        enc_data = cipher.encrypt(pad(data, AES.block_size))
        iv_enc_data = iv + enc_data
        return iv_enc_data

    def decrypt(self, enc_data: bytes) -> bytes:
        assert self.__key is not None

        iv = enc_data[:16]
        encrypted = enc_data[16:]
        bytes_key = bytes(self.__key, "utf-8")
        hashed_key_bytes = sha3_256(bytes_key).digest()
        cipher = AES.new(hashed_key_bytes, AES.MODE_CBC, iv)
        try:
            decrypted = cipher.decrypt(encrypted)
        except Exception as e:
            raise EncryptionDecryptionError(e)
        data = unpad(decrypted, AES.block_size)
        return data
