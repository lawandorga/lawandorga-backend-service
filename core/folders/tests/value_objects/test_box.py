import pytest

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import SymmetricKey
from core.folders.tests.helpers.encryptions import SymmetricEncryptionTest1


class TestKey(SymmetricKey):
    def __init__(self, key: str, origin: str):
        self.__key = key
        self._origin = origin
        super().__init__()

    def get_key(self) -> str:
        return self.__key


@pytest.fixture
def key():
    EncryptionPyramid.reset_encryption_hierarchies()
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    key, version = SymmetricEncryptionTest1.generate_key()
    yield TestKey(key, version)


def test_box_is_bytes(key):
    o1 = OpenBox(data=b"Secret")
    assert o1 == b"Secret"
    assert isinstance(o1, bytes)
    l1 = key.lock(o1)
    assert isinstance(l1, bytes)
    o2 = key.unlock(l1)
    assert o2 == b"Secret"
    assert isinstance(o2, bytes)


def test_box_can_be_unloaded(key):
    o1 = OpenBox(data=b"Secret")
    assert o1 == b"Secret"
    l1 = key.lock(o1)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, encryption_version=key.origin)
    assert enc_data == l2
    o2 = key.unlock(l2)
    assert o2 == b"Secret"


def test_box_decryption_fails_with_another_encryption_class(key):
    o1 = OpenBox(data=b"Secret")
    l1 = key.lock(o1)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, encryption_version="ST0")
    with pytest.raises(ValueError):
        key.unlock(l2)
