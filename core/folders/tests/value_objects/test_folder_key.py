import pytest

from core.folders.domain.value_objects.folder_key import FolderKey
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.tests.helpers.user import UserObject


def test_dict_valid_false(single_encryption):
    owner = UserObject()
    s_key = SymmetricKey.generate()
    key = FolderKey(key=s_key, owner=owner)
    enc_key = key.encrypt_self(owner.get_encryption_key())
    invalid_key = enc_key.invalidate_self()
    d = invalid_key.as_dict()
    new_key = FolderKey.create_from_dict(d, owner)
    assert not new_key.is_valid


def test_dict_valid(single_encryption):
    owner = UserObject()
    s_key = SymmetricKey.generate()
    key = FolderKey(key=s_key, owner=owner)
    enc_key = key.encrypt_self(owner.get_encryption_key())
    d = enc_key.as_dict()
    new_key = FolderKey.create_from_dict(d, owner)
    assert new_key.is_valid


def test_not_equal(single_encryption):
    owner = UserObject()
    s_key = SymmetricKey.generate()
    key = FolderKey(key=s_key, owner=owner)
    enc_key = key.encrypt_self(owner.get_encryption_key())
    invalid_key = enc_key.invalidate_self()
    assert enc_key != invalid_key


def test_raises_error(single_encryption):
    owner = UserObject()
    s_key = SymmetricKey.generate()
    key = FolderKey(key=s_key, owner=owner)
    enc_key = key.encrypt_self(owner.get_encryption_key())
    invalid_key = enc_key.invalidate_self()
    with pytest.raises(ValueError):
        invalid_key.decrypt_self(owner)
    with pytest.raises(ValueError):
        invalid_key.encrypt_self(owner.get_encryption_key())
