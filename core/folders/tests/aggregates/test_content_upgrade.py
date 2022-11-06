from uuid import uuid4

import pytest

from core.folders.domain.aggregates.content_upgrade import ContentUpgrade
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import FolderKey, SymmetricKey
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest2,
    SymmetricEncryptionTest2,
)
from core.folders.tests.helpers.user import UserObject
from core.seedwork.domain_layer import DomainError


def test_encryption_decryption(single_encryption, car_content_key):
    car, content, key = car_content_key

    user = UserObject()

    s_key = SymmetricKey.generate()
    folder_key = FolderKey(
        owner=user,
        key=s_key,
    )

    folder = Folder(
        name="My Folder",
        pk=uuid4(),
        keys=[folder_key.encrypt_self(user.get_encryption_key())],
    )

    upgrade = ContentUpgrade(folder)

    upgrade.add_content(content, key, user)

    content = upgrade.get_content_by_name(content.name)
    content_key = upgrade.get_content_key(content, user)

    content.decrypt(content_key)

    car = content.item
    assert car.name == b"BMW"


def test_with_unknown_content(single_encryption, car_content_key):
    car, content, key = car_content_key
    user = UserObject()

    folder = Folder.create("New Folder")
    folder.grant_access(to=user)
    upgrade = ContentUpgrade(folder=folder)

    with pytest.raises(DomainError):
        upgrade.update_content(content, key, user)

    with pytest.raises(DomainError):
        upgrade.delete_content(content)

    with pytest.raises(DomainError):
        upgrade.get_content_key(content, user)

    with pytest.raises(DomainError):
        upgrade.get_content_by_name("Unknown")


def test_delete_content(single_encryption, car_content_key, upgrade_user):
    upgrade, user = upgrade_user
    car, content, key = car_content_key

    upgrade.delete_content(content)

    with pytest.raises(DomainError):
        upgrade.delete_content(content)


def test_add_content_fails_with_same_name(
    single_encryption, car_content_key, upgrade_user
):
    upgrade, user = upgrade_user
    car, content, key = car_content_key

    with pytest.raises(DomainError):
        upgrade.add_content(content, key, user)


def test_folder_key_not_found(single_encryption, car_content_key, upgrade_user):
    upgrade, user = upgrade_user
    car, content, key = car_content_key
    user2 = UserObject()

    with pytest.raises(DomainError):
        upgrade.get_content_key(content, user2)


def test_reencrypt_all_keys(single_encryption, car_content_key, folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user
    car, content, key = car_content_key
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest2)
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest2)
    assert folder.encryption_version in ["AT1", "ST1"]
    upgrade.update_content(content, key, user)
    assert folder.encryption_version in ["AT2", "ST2"]


def test_reencrypt_works():
    # TODO
    pass
