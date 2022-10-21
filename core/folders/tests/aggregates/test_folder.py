from uuid import uuid4

import pytest

from core.folders.domain.aggregates.content import Content
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.key import FolderKey
from core.folders.tests.helpers.car import CarWithSecretName
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest1,
    AsymmetricEncryptionTest2,
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)

SYMMETRIC_ENCRYPTION_HIERARCHY = {1: SymmetricEncryptionTest1}
CUSTOM_SYMMETRIC_ENCRYPTION_HIERARCHY = {
    1: SymmetricEncryptionTest1,
    2: SymmetricEncryptionTest2,
}

ASYMMETRIC_ENCRYPTION_HIERARCHY = {1: AsymmetricEncryptionTest1}
CUSTOM_ASYMMETRIC_ENCRYPTION_HIERARCHY = {
    1: AsymmetricEncryptionTest1,
    2: AsymmetricEncryptionTest2,
}


@pytest.fixture
def car():
    car = CarWithSecretName(name="BMW")
    content = Content(
        "My Car",
        car,
        SYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    key = content.encrypt()
    yield {"content": content, "key": key}


def test_encryption_decryption(car):
    user = uuid4()
    private_key, public_key = AsymmetricEncryptionTest1.generate_keys()
    folder_key = FolderKey(user, private_key, public_key)

    folder = Folder(
        "My Folder",
        asymmetric_encryption_hierarchy=ASYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    folder.add_content(car["content"], car["key"], folder_key)

    content = folder.get_content_by_name(car["content"].name)
    content_key = folder.get_content_key(content, folder_key)
    content.decrypt(content_key)

    car = content.item
    assert car.name == b"BMW"


def test_encryption_decryption_with_hierarchy(car):
    user_1 = uuid4()
    user_2 = uuid4()
    private_key, public_key = AsymmetricEncryptionTest1.generate_keys()
    folder_key_1 = FolderKey(user_1, private_key, public_key)
    folder_key_2 = FolderKey(user_2, private_key, public_key)

    folder = Folder(
        "My Folder",
        asymmetric_encryption_hierarchy=CUSTOM_ASYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    folder.add_content(car["content"], car["key"], folder_key_1)
    content = folder.get_content_by_name(car["content"].name)
    content_key = folder.get_content_key(content, folder_key_1)
    content.decrypt(content_key)

    car = content.item
    car.name = b"Audi"

    new_key = content.encrypt()
    folder.update_content(content, new_key, folder_key_1)

    assert (
        new_key.get_key().encode("utf-8")
        in AsymmetricEncryptionTest2.get_treasure_chest().values()
    )
    content = folder.get_content_by_name(content.name)
    content_key = folder.get_content_key(content, folder_key_2)
    content.decrypt(content_key)

    assert car.name == b"Audi"
