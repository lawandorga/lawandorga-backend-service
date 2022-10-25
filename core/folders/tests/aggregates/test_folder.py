from uuid import uuid4

import pytest

from core.folders.domain.aggregates.content import Content
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import FolderKey
from core.folders.tests.helpers.car import CarWithSecretName
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest1,
    AsymmetricEncryptionTest2,
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)
from core.folders.tests.helpers.user import UserObject


@pytest.fixture
def encryption_reset():
    EncryptionPyramid.reset_encryption_hierarchies()
    yield


@pytest.fixture
def single_encryption(encryption_reset):
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    yield


@pytest.fixture
def double_encryption(encryption_reset):
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest2)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionTest2)
    yield


@pytest.fixture
def car_content_key():
    car = CarWithSecretName(name="BMW")
    content = Content(
        "My Car",
        car,
    )
    key = content.encrypt()
    yield car, content, key


def test_encryption_decryption(single_encryption, car_content_key):
    car, content, key = car_content_key

    user = UserObject()

    private_key, public_key, version = AsymmetricEncryptionTest1.generate_keys()
    folder_key = FolderKey.create(
        owner=user,
        private_key=private_key,
        public_key=public_key,
        origin=version,
    )

    folder = Folder(name="My Folder", pk=uuid4(), keys=[folder_key])
    folder.add_content(content, key, user)

    content = folder.get_content_by_name(content.name)
    content_key = folder.get_content_key(content, user)
    content.decrypt(content_key)

    car = content.item
    assert car.name == b"BMW"


def test_encryption_decryption_with_hierarchy(single_encryption, car_content_key):
    user_1 = UserObject()
    user_2 = UserObject()
    private_key, public_key, version = AsymmetricEncryptionTest1.generate_keys()
    folder_key_1 = FolderKey.create(
        owner=user_1,
        private_key=private_key,
        public_key=public_key,
        origin=version,
    )
    folder_key_2 = FolderKey.create(
        owner=user_2,
        private_key=private_key,
        public_key=public_key,
        origin=version,
    )
    folder = Folder(name="My Folder", pk=uuid4(), keys=[folder_key_1, folder_key_2])

    car, content, key = car_content_key
    folder.add_content(content, key, user_1)

    content = folder.get_content_by_name(content.name)
    content_key = folder.get_content_key(content, user_2)
    content.decrypt(content_key)

    car = content.item
    car.name = b"Audi"

    new_key = content.encrypt()
    folder.update_content(content, new_key, user_2)

    content = folder.get_content_by_name(content.name)
    content_key = folder.get_content_key(content, user_1)
    content.decrypt(content_key)

    assert car.name == b"Audi"


def test_keys_are_regenerated(double_encryption, car_content_key):
    car, content, key = car_content_key
    user = UserObject()

    private_key, public_key, version = AsymmetricEncryptionTest1.generate_keys()
    folder_key = FolderKey.create(
        owner=user,
        private_key=private_key,
        public_key=public_key,
        origin=version,
    )
    folder = Folder(name="My Folder", pk=uuid4(), keys=[folder_key])
    folder.add_content(content, key, user)

    assert (
        key.get_key().encode("utf-8")
        in AsymmetricEncryptionTest2.get_treasure_chest().values()
    )

    enc_content = folder.get_content_by_name("My Car")
    key = folder.get_content_key(enc_content, user)

    enc_content.decrypt(key)
    car = content.item

    assert car.name == b"BMW"
    assert folder.encryption_version == "AT2"
