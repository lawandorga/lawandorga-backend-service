import os
from uuid import uuid4

from core.folders.domain.value_objects.encryption import SymmetricEncryption


class SymmetricEncryptionTest1(SymmetricEncryption):
    __SECRETS: dict[bytes, bytes] = {}

    def __init__(self, key: str):
        self.__key = key
        super().__init__()

    @staticmethod
    def get_treasure_chest():
        return SymmetricEncryptionTest1.__SECRETS

    @staticmethod
    def generate_key() -> str:
        return str(os.urandom(1))

    def encrypt(self, data: bytes) -> bytes:
        uuid = bytes(str(uuid4()), "utf-8")
        place = uuid + bytes(self.__key, "utf-8")
        self.__class__.get_treasure_chest()[place] = data
        return uuid

    def decrypt(self, enc_data: bytes) -> bytes:
        uuid = enc_data
        place = uuid + bytes(self.__key, "utf-8")
        data = self.__class__.get_treasure_chest().pop(place)
        return data


class SymmetricEncryptionTest2(SymmetricEncryptionTest1):
    __SECRETS_2: dict[bytes, bytes] = {}

    @staticmethod
    def get_treasure_chest():
        return SymmetricEncryptionTest2.__SECRETS_2
