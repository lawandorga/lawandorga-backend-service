import pytest

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.keys import SymmetricKey
from core.folders.tests.helpers.encryptions import (
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)


class TestKey(SymmetricKey):
    def __init__(self, key: str):
        self.__key = key

    def get_key(self) -> str:
        return self.__key


@pytest.fixture
def key():
    yield TestKey(SymmetricEncryptionTest1.generate_key())


def test_box_is_bytes(key):
    o1 = OpenBox(data=b"Secret")
    assert o1 == b"Secret"
    assert isinstance(o1, bytes)
    l1 = o1.lock(key, encryption_class=SymmetricEncryptionTest1)
    assert isinstance(l1, bytes)
    o2 = l1.unlock(key)
    assert o2 == b"Secret"
    assert isinstance(o2, bytes)


def test_box_can_be_unloaded(key):
    o1 = OpenBox(data=b"Secret")
    assert o1 == b"Secret"
    l1 = o1.lock(key, encryption_class=SymmetricEncryptionTest1)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, encryption_class=SymmetricEncryptionTest1)
    assert enc_data == l2
    o2 = l2.unlock(key)
    assert o2 == b"Secret"


def test_box_decryption_fails_with_another_encryption_class(key):
    o1 = OpenBox(data=b"Secret")
    l1 = o1.lock(key, encryption_class=SymmetricEncryptionTest1)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, encryption_class=SymmetricEncryptionTest2)
    with pytest.raises(KeyError):
        l2.unlock(key)
