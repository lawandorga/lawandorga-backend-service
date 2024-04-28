from typing import Optional
from uuid import uuid4

import pytest

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.item import Item
from core.folders.domain.value_objects.folder_key import (
    EncryptedFolderKeyOfUser,
    FolderKey,
)
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.tests.test_helpers.encryptions import (
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)
from core.folders.tests.test_helpers.user import ForeignUserObject, UserObject
from core.seedwork.domain_layer import DomainError


def test_grant_access():
    user = UserObject()

    folder = Folder.create("New Folder")
    folder.grant_access(to=user)

    assert folder.has_access(user)


def test_grant_access_to_another_user():
    user1 = UserObject()
    user2 = UserObject()

    folder = Folder.create("New Folder")
    folder.grant_access(to=user1)
    folder.grant_access(to=user2, by=user1)

    assert folder.has_access(user2)


def test_encryption_version():
    folder = Folder.create("Test")
    assert folder.encryption_version is None
    user = UserObject()
    folder.grant_access(to=user)
    assert folder.encryption_version == "A1" or folder.encryption_version == "S1"

    s_key = SymmetricKey.generate(SymmetricEncryptionTest1)
    folder_key_1 = FolderKey(
        owner_uuid=user.uuid,
        key=s_key,
    )
    s_key = SymmetricKey.generate(SymmetricEncryptionTest2)
    folder_key_2 = FolderKey(
        owner_uuid=user.uuid,
        key=s_key,
    )
    folder = Folder(
        name="Test",
        uuid=uuid4(),
        keys=[
            EncryptedFolderKeyOfUser.create_from_key(
                folder_key_1, user.get_encryption_key()
            ),
            EncryptedFolderKeyOfUser.create_from_key(
                folder_key_2, user.get_encryption_key()
            ),
        ],
    )
    with pytest.raises(Exception):
        assert folder.encryption_version


def test_update_information(folder_user):
    folder, user = folder_user
    folder.update_information(name="New Name")
    assert folder.name == "New Name"


def test_folder_key_decryption_error():
    user1 = ForeignUserObject()
    key = FolderKey(
        key=SymmetricKey.generate(SymmetricEncryptionTest1), owner_uuid=user1.uuid
    )
    enc_key = EncryptedFolderKeyOfUser.create_from_key(key, user1.get_encryption_key())
    user2 = UserObject()
    with pytest.raises(KeyError):
        enc_key.decrypt_self(user2)


def test_folder_key_str_method():
    user1 = UserObject()
    key = FolderKey(
        owner_uuid=user1.uuid, key=SymmetricKey.generate(SymmetricEncryptionTest1)
    )
    assert str(key) == "FolderKey of '{}'".format(user1.uuid)


def test_folder_access():
    user_1 = UserObject()
    user_2 = UserObject()

    s_key = SymmetricKey.generate(SymmetricEncryptionTest1)
    folder_key_1 = FolderKey(
        owner_uuid=user_1.uuid,
        key=s_key,
    )
    folder_key_2 = FolderKey(
        owner_uuid=user_2.uuid,
        key=s_key,
    )

    folder = Folder(
        name="My Folder",
        uuid=uuid4(),
        keys=[
            EncryptedFolderKeyOfUser.create_from_key(
                folder_key_1, user_1.get_encryption_key()
            ),
            EncryptedFolderKeyOfUser.create_from_key(
                folder_key_2, user_2.get_encryption_key()
            ),
        ],
    )

    assert folder.has_access(user_1) and folder.has_access(user_2)


def test_has_no_access():
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
    one_more = UserObject()

    folder.grant_access(another_user, user)
    folder.grant_access(one_more, user)
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
        self.folder_uuid = folder.uuid
        self.__folder = folder


def test_item(folder_user):
    folder, user = folder_user
    item = CustomItem()
    item.set_folder(folder)
    folder.add_item(item)
    assert item.uuid in [i.uuid for i in folder.items] and item.folder == folder
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


def disabled_test_folder_move(folder_user):
    folder_1, user = folder_user
    folder_2 = Folder.create("Child")
    folder_2.grant_access(user)
    folder_2.set_parent(folder_1, user)
    folder_3 = Folder.create("Parent")
    folder_3.grant_access(user)
    folder_2.move(folder_3, user)
    assert folder_2.parent == folder_3


def disabled_test_folder_move_and_access():
    folder_1 = Folder.create("1")
    user_1 = UserObject()
    folder_2 = Folder.create("2")
    user_2 = UserObject()
    folder_3 = Folder.create("3")
    #
    folder_1.grant_access(user_1)
    folder_2.set_parent(folder_1, user_1)
    folder_3.grant_access(user_1)
    folder_3.grant_access(user_2, user_1)
    assert not folder_2.has_access(user_2)
    folder_2.move(folder_3, user_1)
    assert folder_2.has_access(user_2)


def test_folder_move_errors():
    folder_1 = Folder.create("1")
    user_1 = UserObject()
    folder_2 = Folder.create("2")
    user_2 = UserObject()
    folder_3 = Folder.create("3")
    user_3 = UserObject()
    #
    folder_1.grant_access(user_1)
    folder_2.set_parent(folder_1, user_1)
    folder_3.grant_access(user_2)
    with pytest.raises(DomainError):
        folder_2.move(folder_3, user_1)
    with pytest.raises(DomainError):
        folder_2.move(folder_3, user_1)
    with pytest.raises(DomainError):
        folder_2.move(folder_3, user_3)


def test_folder_init_without_keys():
    user = UserObject()
    folder_1 = Folder.create("1")
    folder_2 = Folder.create("2")
    with pytest.raises(AssertionError):
        folder_2.set_parent(folder_1, user)


def test_folder_move_inside_child_error():
    user = UserObject()
    folder_1 = Folder.create("1")
    folder_1.grant_access(user)
    folder_2 = Folder.create("2")
    folder_2.set_parent(folder_1, user)
    folder_3 = Folder.create("3")
    folder_3.set_parent(folder_2, user)
    with pytest.raises(DomainError):
        folder_1.move(folder_3, user)


def test_folder_restricted():
    folder = Folder.create("3")
    folder.restrict()
    assert folder.restricted is True
    with pytest.raises(DomainError):
        folder.update_information(name="New Name")


def test_folder_name_change_with_force():
    folder = Folder.create("5")
    folder.restrict()
    assert folder.restricted is True
    folder.update_information(name="New Name", force=True)
    assert folder.name == "New Name"


def test_restricted_folder_can_not_have_children():
    user = UserObject()
    folder1 = Folder.create("3")
    folder1.grant_access(user)
    folder1.restrict()
    folder2 = Folder.create("4")
    with pytest.raises(DomainError):
        folder2.set_parent(folder1, user)
