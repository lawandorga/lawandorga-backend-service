import pytest

from core.folders.domain.value_objects.folder_key import (
    EncryptedFolderKeyOfUser,
    FolderKey,
)
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.tests.test_helpers.encryptions import SymmetricEncryptionTest1
from core.folders.tests.test_helpers.user import UserObject


def test_dict_valid_false():
    owner = UserObject()
    s_key = SymmetricKey.generate(SymmetricEncryptionTest1)
    key = FolderKey(key=s_key, owner_uuid=owner.uuid)
    enc_key = EncryptedFolderKeyOfUser.create_from_key(key, owner.get_encryption_key())
    invalid_key = enc_key.invalidate_self()
    d = invalid_key.as_dict()
    new_key = EncryptedFolderKeyOfUser.create_from_dict(d)
    assert not new_key.is_valid


def test_dict_valid():
    owner = UserObject()
    s_key = SymmetricKey.generate(SymmetricEncryptionTest1)
    key = FolderKey(key=s_key, owner_uuid=owner.uuid)
    enc_key = EncryptedFolderKeyOfUser.create_from_key(key, owner.get_encryption_key())
    d = enc_key.as_dict()
    new_key = EncryptedFolderKeyOfUser.create_from_dict(d)
    assert new_key.is_valid


def test_not_equal():
    owner = UserObject()
    s_key = SymmetricKey.generate(SymmetricEncryptionTest1)
    key = FolderKey(key=s_key, owner_uuid=owner.uuid)
    enc_key = EncryptedFolderKeyOfUser.create_from_key(key, owner.get_encryption_key())
    invalid_key = enc_key.invalidate_self()
    assert enc_key != invalid_key


def test_raises_error():
    owner = UserObject()
    s_key = SymmetricKey.generate(SymmetricEncryptionTest1)
    key = FolderKey(key=s_key, owner_uuid=owner.uuid)
    enc_key = EncryptedFolderKeyOfUser.create_from_key(key, owner.get_encryption_key())
    invalid_key = enc_key.invalidate_self()
    with pytest.raises(ValueError):
        invalid_key.decrypt_self(owner)
    with pytest.raises(ValueError):
        invalid_key.decrypt_self(owner)
