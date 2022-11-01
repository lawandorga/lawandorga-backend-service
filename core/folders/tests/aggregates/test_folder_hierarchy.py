import pytest

from core.folders.domain.aggregates.content import Content
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.value_objects.encryption import EncryptionPyramid
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


@pytest.fixture
def folder_user(car_content_key):
    car, content, key = car_content_key
    user = UserObject()
    folder = Folder.create("New Folder")
    folder.grant_access(to=user)
    folder.add_content(content, key, user)
    yield folder, user


def test_hierarchy(single_encryption, car_content_key):
    car1, content1, key1 = car_content_key

    user = UserObject()

    folder1 = Folder.create("Parent")
    folder1.grant_access(to=user)

    folder2 = Folder.create("Child")
    folder2.set_parent(folder1, user)
    folder2.add_content(content1, key1, user)

    content2 = folder2.get_content_by_name("My Car")
    key2 = folder2.get_content_key(content2, user)
    content2.decrypt(key2)
    car2 = content2.item

    assert car2.name == b"BMW"
