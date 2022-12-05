from uuid import uuid4

import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    FolderKey,
    SymmetricKey,
)
from core.folders.tests.helpers.encryptions import SymmetricEncryptionTest2
from core.folders.tests.helpers.user import ForeignUserObject, UserObject


def test_keys_are_regenerated(single_encryption, car_content_key):
    user = UserObject()

    folder_key = FolderKey(owner=user, key=SymmetricKey.generate())
    folder = Folder(
        name="My Folder",
        pk=uuid4(),
        keys=[folder_key.encrypt_self(user.get_encryption_key())],
    )

    assert folder.encryption_version == "ST1"

    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest2)
    folder.check_encryption_version(user)

    assert folder.encryption_version == "ST2"


def test_grant_access(single_encryption, car_content_key):
    user = UserObject()

    folder = Folder.create("New Folder")
    folder.grant_access(to=user)

    assert folder.has_access(user)


def test_grant_access_to_another_user(single_encryption, car_content_key):
    user1 = UserObject()
    user2 = UserObject()

    folder = Folder.create("New Folder")
    folder.grant_access(to=user1)
    folder.grant_access(to=user2, by=user1)

    assert folder.has_access(user2)


def test_encryption_version(single_encryption):
    folder = Folder.create("Test")
    assert folder.encryption_version is None
    user = UserObject()
    folder.grant_access(to=user)
    assert folder.encryption_version == "AT1" or folder.encryption_version == "ST1"

    s_key = SymmetricKey.generate()
    folder_key_1 = FolderKey(
        owner=user,
        key=s_key,
    )
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest2)
    s_key = SymmetricKey.generate()
    folder_key_2 = FolderKey(
        owner=user,
        key=s_key,
    )
    folder = Folder(
        name="Test",
        pk=uuid4(),
        keys=[
            folder_key_1.encrypt_self(user.get_encryption_key()),
            folder_key_2.encrypt_self(user.get_encryption_key()),
        ],
    )
    with pytest.raises(Exception):
        assert folder.encryption_version


def test_move(single_encryption, folder_user):
    folder, user = folder_user
    folder.move(None)


def test_update_information(single_encryption, folder_user):
    folder, user = folder_user
    folder.update_information(name="New Name")
    assert folder.name == "New Name"


def test_str_method():
    folder = Folder.create("Test")
    assert str(folder) == "Folder Test"


def test_folder_key_decryption_error(single_encryption):
    user1 = ForeignUserObject()
    key = FolderKey(key=SymmetricKey.generate(), owner=user1)
    enc_key = key.encrypt_self(user1.get_encryption_key())
    user2 = UserObject()
    with pytest.raises(ValueError):
        enc_key.decrypt_self(user2)


def test_folder_key_str_method(single_encryption):
    user1 = UserObject()
    key = FolderKey(owner=user1, key=AsymmetricKey.generate())
    assert str(key) == "FolderKey of {}".format(user1.uuid)


def test_folder_access(single_encryption, car_content_key):
    user_1 = UserObject()
    user_2 = UserObject()

    s_key = SymmetricKey.generate()
    folder_key_1 = FolderKey(
        owner=user_1,
        key=s_key,
    )
    folder_key_2 = FolderKey(
        owner=user_2,
        key=s_key,
    )

    folder = Folder(
        name="My Folder",
        pk=uuid4(),
        keys=[
            folder_key_1.encrypt_self(user_1.get_encryption_key()),
            folder_key_2.encrypt_self(user_2.get_encryption_key()),
        ],
    )

    assert folder.has_access(user_1) and folder.has_access(user_2)


def test_has_no_access(single_encryption):
    user1 = UserObject()
    user2 = UserObject()
    folder = Folder.create("Test")
    folder.grant_access(user2)
    assert not folder.has_access(user1)
