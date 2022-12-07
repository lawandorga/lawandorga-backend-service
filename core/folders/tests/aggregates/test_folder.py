from typing import Optional
from uuid import uuid4

import pytest

from core.folders.domain.aggregates.folder import Folder, Item
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    FolderKey,
    SymmetricKey,
)
from core.folders.tests.helpers.encryptions import SymmetricEncryptionTest2
from core.folders.tests.helpers.user import ForeignUserObject, UserObject
from core.seedwork.domain_layer import DomainError


def todo_test_keys_are_regenerated():
    user = UserObject()

    folder_key = FolderKey(owner=user, key=SymmetricKey.generate())
    folder = Folder(
        name="My Folder",
        uuid=uuid4(),
        keys=[folder_key.encrypt_self(user.get_encryption_key())],
    )

    assert folder.encryption_version == "ST1"

    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest2)
    folder.check_encryption_version(user)

    assert folder.encryption_version == "ST2"


def test_grant_access(single_encryption):
    user = UserObject()

    folder = Folder.create("New Folder")
    folder.grant_access(to=user)

    assert folder.has_access(user)


def test_grant_access_to_another_user(single_encryption):
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
        uuid=uuid4(),
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


def test_folder_access(single_encryption):
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
        uuid=uuid4(),
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


def test_grant_access_twice(folder_user):
    folder, user = folder_user
    with pytest.raises(DomainError):
        folder.grant_access(user, user)


def test_revoke_access(folder_user):
    folder, user = folder_user
    another_user = UserObject()

    folder.grant_access(another_user, user)
    folder.revoke_access(user)

    assert not folder.has_access(user)


def test_revoke_access_errors(folder_user):
    folder, user = folder_user
    another_user = UserObject()

    with pytest.raises(DomainError):
        folder.revoke_access(another_user)

    with pytest.raises(DomainError):
        folder.revoke_access(user)


def test_as_dict(folder):
    d = folder.as_dict()
    assert d["name"] == folder.name


def test_parent_uuid(folder_user):
    folder, user = folder_user
    another_folder = Folder.create("Folder 2", org_pk=folder.org_pk)
    another_folder.set_parent(folder, user)
    assert another_folder.parent_uuid == folder.uuid
    assert folder.parent_uuid is None


class CustomItem(Item):
    __folder: Optional[Folder]
    folder_uuid = None
    name = "CustomItem"
    REPOSITORY = "NONE"

    def __init__(self):
        self.uuid = uuid4()

    @property
    def folder(self) -> Optional["Folder"]:
        return self.__folder

    def set_folder(self, folder: "Folder"):
        super().set_folder(folder)
        self.__folder = folder


def test_item(folder_user):
    folder, user = folder_user
    item = CustomItem()

    folder.add_item(item)
    assert item in folder.items and item.folder == folder
    folder.remove_item(item)
    assert item not in folder.items


def test_set_parent(folder_user):
    folder, user = folder_user
    another_user = UserObject()
    folder.grant_access(another_user, user)

    another_folder = Folder.create("Test Folder")

    another_folder.grant_access(user)
    another_folder.set_parent(folder, user)

    assert another_folder.has_access(another_user)


def test_get_encryption_key(folder_user):
    folder, user = folder_user
    another_user = UserObject()
    another_folder = Folder.create("Another")
    another_folder.set_parent(folder, user)
    folder.grant_access(another_user, user)
    another_folder.get_encryption_key(requestor=another_user)
