import os
from uuid import uuid4

import pytest

from apps.core.folders.domain.value_objects.box import LockedBox, OpenBox
from apps.core.folders.domain.value_objects.encryption import SymmetricEncryption
from apps.core.folders.domain.value_objects.key import SymmetricKey


class SymmetricEncryptionTest1(SymmetricEncryption):
    __SECRETS: dict[bytes, bytes] = {}

    def __init__(self, key: str):
        self.__key = key

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
        data = self.__class__.get_treasure_chest()[place]
        return data


class SymmetricEncryptionTest2(SymmetricEncryptionTest1):
    __SECRETS: dict[bytes, bytes] = {}

    @staticmethod
    def get_treasure_chest():
        return SymmetricEncryptionTest2.__SECRETS


class TestKey(SymmetricKey):
    def __init__(self, key: str):
        self.__key = key

    def get_key(self) -> str:
        return self.__key


@pytest.fixture
def key():
    yield TestKey(SymmetricEncryptionTest1.generate_key())


def test_box_is_bytes(key):
    o1 = OpenBox(data=b"Secret", encryption_class=SymmetricEncryptionTest1)
    assert o1 == b"Secret"
    assert isinstance(o1, bytes)
    l1 = o1.lock(key)
    assert isinstance(l1, bytes)
    o2 = l1.unlock(key)
    assert o2 == b"Secret"
    assert isinstance(o2, bytes)


def test_box_can_be_unloaded(key):
    o1 = OpenBox(data=b"Secret", encryption_class=SymmetricEncryptionTest1)
    assert o1 == b"Secret"
    l1 = o1.lock(key)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, encryption_class=SymmetricEncryptionTest1)
    assert enc_data == l2
    o2 = l2.unlock(key)
    assert o2 == b"Secret"


def test_box_decryption_fails_with_another_encryption_class(key):
    o1 = OpenBox(data=b"Secret", encryption_class=SymmetricEncryptionTest1)
    l1 = o1.lock(key)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, encryption_class=SymmetricEncryptionTest2)
    with pytest.raises(KeyError):
        l2.unlock(key)
