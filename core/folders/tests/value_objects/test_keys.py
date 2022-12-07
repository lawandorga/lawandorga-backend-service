import pytest

from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest1,
    SymmetricEncryptionTest1,
)


@pytest.fixture
def encryption():
    EncryptionWarehouse.reset_encryption_hierarchies()
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest1)


@pytest.fixture
def s_key(encryption):
    yield SymmetricKey.generate()


@pytest.fixture
def a_key(encryption):
    yield AsymmetricKey.generate()


@pytest.fixture
def box():
    yield OpenBox(data=b"Test")


def test_symmetric_dict(s_key):
    key_1 = SymmetricKey.generate()
    enc_key_1 = EncryptedSymmetricKey.create(key_1, s_key)
    dict_enc_key_1 = enc_key_1.as_dict()
    enc_key_2 = EncryptedSymmetricKey.create_from_dict(dict_enc_key_1)
    assert enc_key_1 == enc_key_2
    key_2 = enc_key_2.decrypt(s_key)
    assert key_1 == key_2


def test_asymmetric_dict(s_key):
    key_1 = AsymmetricKey.generate()
    enc_key_1 = EncryptedAsymmetricKey.create(key_1, s_key)
    dict_enc_key_1 = enc_key_1.as_dict()
    enc_key_2 = EncryptedAsymmetricKey.create_from_dict(dict_enc_key_1)
    assert enc_key_1 == enc_key_2
    key_2 = enc_key_2.decrypt(s_key)
    assert key_1 == key_2


def test_unlock_error(s_key, a_key):
    key_1 = AsymmetricKey.generate()
    enc_key_1 = EncryptedAsymmetricKey.create(key_1, s_key)
    with pytest.raises(ValueError):
        enc_key_1.decrypt(a_key)


def test_encrypted_symmetric_keys_errors(s_key):
    box = OpenBox(data=b"Test")
    key = SymmetricKey.generate()
    locked_box = key.lock(box)
    enc_key = EncryptedSymmetricKey.create(key, s_key)
    with pytest.raises(ValueError):
        enc_key.lock(box)
    with pytest.raises(ValueError):
        enc_key.get_encryption()
    with pytest.raises(ValueError):
        enc_key.unlock(locked_box)


def test_asymmetric_key_errors(a_key, box):
    key = AsymmetricKey.generate()
    locked_box = key.lock(box)
    enc_key = EncryptedAsymmetricKey.create(key, a_key)
    with pytest.raises(ValueError):
        enc_key.unlock(locked_box)

    key = EncryptedAsymmetricKey(public_key=key.get_public_key(), origin=key.origin)
    with pytest.raises(ValueError):
        key.as_dict()
    with pytest.raises(ValueError):
        key.decrypt(a_key)


def test_encrypted_asymmetric_key_can_encrypt(a_key, box):
    key = AsymmetricKey.generate()
    enc_key = EncryptedAsymmetricKey.create(key, a_key)
    locked_box = enc_key.lock(box)
    key = enc_key.decrypt(a_key)
    box2 = key.unlock(locked_box)
    assert box == box2


def test_equality_false(a_key, s_key):
    assert not a_key == s_key
    assert not s_key == a_key
    assert not a_key == "test"
    assert not s_key == "test"
