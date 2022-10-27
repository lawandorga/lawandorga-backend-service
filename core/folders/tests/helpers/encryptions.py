import os
from typing import Tuple
from uuid import uuid4

from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)


class AsymmetricEncryptionTest1(AsymmetricEncryption):
    VERSION = "AT1"
    __SECRETS: dict[str, bytes] = {}
    __KEYS: dict[str, str] = {}

    def __init__(self, private_key: str, public_key: str):
        self.__private_key = private_key
        self.__public_key = public_key
        self.__class__.get_keys()[private_key] = public_key
        super().__init__()

    @staticmethod
    def get_treasure_chest():
        return AsymmetricEncryptionTest1.__SECRETS

    @staticmethod
    def get_keys():
        return AsymmetricEncryptionTest1.__KEYS

    @classmethod
    def generate_keys(cls) -> Tuple[str, str, str]:
        return str(os.urandom(1)), str(os.urandom(1)), cls.VERSION

    def encrypt(self, data: bytes) -> bytes:
        uuid = bytes(str(uuid4()), "utf-8")
        place = uuid + bytes(self.__public_key, "utf-8")
        self.__class__.get_treasure_chest()[place] = data
        return uuid

    def decrypt(self, enc_data: bytes) -> bytes:
        uuid = enc_data
        place = uuid + bytes(self.__class__.get_keys()[self.__private_key], "utf-8")
        data = self.__class__.get_treasure_chest()[place]
        return data


class AsymmetricEncryptionTest2(AsymmetricEncryptionTest1):
    VERSION = "AT2"
    __SECRETS_2: dict[str, bytes] = {}
    __KEYS_2: dict[str, str] = {}

    @staticmethod
    def get_treasure_chest():
        return AsymmetricEncryptionTest2.__SECRETS_2

    @staticmethod
    def get_keys():
        return AsymmetricEncryptionTest2.__KEYS_2


class SymmetricEncryptionTest1(SymmetricEncryption):
    VERSION = "ST1"
    __SECRETS: dict[bytes, bytes] = {}

    def __init__(self, key: str):
        self.__key = key
        super().__init__()

    @staticmethod
    def get_treasure_chest():
        return SymmetricEncryptionTest1.__SECRETS

    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        return str(os.urandom(1)), cls.VERSION

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
    VERSION = "ST2"
    __SECRETS_2: dict[bytes, bytes] = {}

    @staticmethod
    def get_treasure_chest():
        return SymmetricEncryptionTest2.__SECRETS_2
