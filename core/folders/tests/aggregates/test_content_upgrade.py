from uuid import uuid4

import pytest

from core.folders.domain.aggregates.content_upgrade import ContentUpgrade
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
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

    upgrade = ContentUpgrade(folder=folder)

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
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest2)
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest2)
    assert folder.encryption_version in ["AT1", "ST1"]
    upgrade.update_content(content, key, user)
    assert folder.encryption_version in ["AT2", "ST2"]


def test_reencrypt_works(single_encryption, folder_upgrade_user):
    folder, upgrade, user = folder_upgrade_user

    content2 = upgrade.get_content_by_name("My Car")
    key2 = upgrade.get_content_key(content2, user)
    content2.decrypt(key2)
    car2 = content2.item
    assert car2.name == b"BMW"
    key2 = content2.encrypt()
    upgrade.update_content(content2, key2, user)
    assert folder.encryption_version == "ST1" and upgrade.encryption_version == "ST1"

    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest2)

    folder.check_encryption_version(user)
    assert folder.encryption_version == "ST2" and upgrade.encryption_version == "ST2"

    content3 = upgrade.get_content_by_name("My Car")
    key3 = upgrade.get_content_key(content3, user)
    content3.decrypt(key3)
    car3 = content3.item
    assert car3.name == b"BMW"
