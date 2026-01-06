import pickle

import pytest

from core.encryption.value_objects.box import Box, LockedBox, OpenBox
from core.encryption.value_objects.symmetric_key import SymmetricKey
from core.folders.tests.test_helpers.encryptions import SymmetricEncryptionTest1


@pytest.fixture
def key():
    key, version = SymmetricEncryptionTest1.generate_key()
    yield SymmetricKey.create(key=key, origin=version)


def test_box_can_be_pickled():
    o1 = OpenBox(data=b"Data")
    pickled = pickle.dumps(o1)
    o2 = pickle.loads(pickled)
    assert o1 == o2


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
    l2 = LockedBox(enc_data=enc_data, key_origin=key.origin)
    assert enc_data == l2
    o2 = key.unlock(l2)
    assert o2 == b"Secret"


def test_box_decryption_fails_with_another_encryption_class(key):
    o1 = OpenBox(data=b"Secret")
    l1 = key.lock(o1)
    enc_data = l1.value
    l2 = LockedBox(enc_data=enc_data, key_origin="ST0")
    with pytest.raises(ValueError):
        key.unlock(l2)


def test_repr():
    o1 = OpenBox(data=b"Data")
    o2 = LockedBox(enc_data=b"EncData", key_origin="ST1")
    assert repr(o1) == "OpenBox(b'Data')"
    assert repr(o2) == "LockedBox(b'EncData', 'ST1')"


def test_box_error():
    with pytest.raises(TypeError):
        Box(data=b"abc", enc_data=b"abc")


def test_data():
    o1 = OpenBox(data=b"Data")
    o2 = LockedBox(enc_data=b"EncData", key_origin="ST1")
    assert o1.value == b"Data"
    assert o2.value == b"EncData"


def test_decryption_error(key):
    lb = LockedBox(enc_data=b"EncData", key_origin="SUNKNOWN")
    with pytest.raises(ValueError):
        key.unlock(lb)


def test_open_box_dict():
    b1 = OpenBox(data=b"Open")
    b_dict = b1.as_dict()
    b2 = OpenBox.create_from_dict(b_dict)
    assert b1 == b2


def test_closed_box_dict(key):
    o1 = OpenBox(data=b"Open")
    l1 = key.lock(o1)
    l1_dict = l1.as_dict()
    l2 = LockedBox.create_from_dict(l1_dict)
    assert l1 == l2
    o2 = key.unlock(l2)
    assert o1 == o2


def test_equality_false(key):
    o1 = OpenBox(data=b"Open")
    l1 = key.lock(o1)

    assert not o1 == l1
    assert not l1 == o1
    assert not l1 == b"Open"
    assert not o1 == "Open"


def test_bytes_equality():
    o1 = OpenBox(data=b"Open")
    assert o1 == b"Open"
