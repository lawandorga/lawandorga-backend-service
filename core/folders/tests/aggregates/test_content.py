from core.folders.domain.aggregates.content import Content
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.tests.helpers.car import CarWithSecretName
from core.folders.tests.helpers.encryptions import (
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)
import pytest


@pytest.fixture
def encryption_reset():
    EncryptionPyramid.reset_encryption_hierarchies()
    yield


@pytest.fixture
def single_encryption(encryption_reset):
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    yield


@pytest.fixture
def double_encryption(encryption_reset):
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionTest2)
    yield


@pytest.fixture
def car_content_key():
    car = CarWithSecretName(name="Secret Antique")
    content = Content(
        "My Car",
        car,
    )
    assert car.name == b"Secret Antique"
    key = content.encrypt()
    yield car, content, key


def test_encrypt_and_decrypt(single_encryption, car_content_key):
    car, content, key = car_content_key
    assert isinstance(car.name, LockedBox)
    assert car.name != b"Secret Antique"
    content.decrypt(key)
    assert isinstance(car.name, OpenBox)
    assert car.name == b"Secret Antique"


def test_encryption_hierarchy_works_in_simple_case(double_encryption, car_content_key):
    car, content, key = car_content_key

    assert isinstance(car.name, LockedBox)
    assert car.name != b"Secret Antique"
    content.decrypt(key)
    assert isinstance(car.name, OpenBox)
    assert car.name == b"Secret Antique"
    assert (
        b"Secret Antique" not in SymmetricEncryptionTest1.get_treasure_chest().values()
    )
    assert (
        b"Secret Antique" not in SymmetricEncryptionTest2.get_treasure_chest().values()
    )
    content.encrypt()
    assert b"Secret Antique" in SymmetricEncryptionTest2.get_treasure_chest().values()


def test_encryption_hierarchy_works_after_new_init(double_encryption, car_content_key):
    car, content, key = car_content_key

    content = Content("My Car", car, content.encryption_version)
    content.decrypt(key)

    assert isinstance(car.name, OpenBox)
    assert car.name == b"Secret Antique"

    content.encrypt()
    assert content.encryption_version == "ST2"
    assert b"Secret Antique" in SymmetricEncryptionTest2.get_treasure_chest().values()
    assert (
        b"Secret Antique" not in SymmetricEncryptionTest1.get_treasure_chest().values()
    )


def test_content_after_encryption(double_encryption, car_content_key):
    car, content, key = car_content_key

    car2 = CarWithSecretName(enc_name=car.name)
    content = Content(
        "My Car", car2, content.encryption_version
    )
    content.decrypt(key)

    assert car2.name == b"Secret Antique"
