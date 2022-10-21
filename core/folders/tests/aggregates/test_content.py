from core.folders.domain.aggregates.content import Content
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.tests.helpers.car import CarWithSecretName
from core.folders.tests.helpers.encryptions import (
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)

SYMMETRIC_ENCRYPTION_HIERARCHY = {1: SymmetricEncryptionTest1}
CUSTOM_ENCRYPTION_HIERARCHY = {
    1: SymmetricEncryptionTest1,
    2: SymmetricEncryptionTest2,
}


def test_encrypt_and_decrypt():
    car = CarWithSecretName(name="Secret Antique")
    content = Content(
        "My Car",
        car,
        SYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    assert car.name == b"Secret Antique"
    _key = content.encrypt()
    assert isinstance(car.name, LockedBox)
    assert car.name != b"Secret Antique"
    content.decrypt(_key)
    assert isinstance(car.name, OpenBox)
    assert car.name == b"Secret Antique"


def test_encryption_hierarchy_works_in_simple_case():
    car = CarWithSecretName(name="Secret Antique")
    content = Content(
        "My Car",
        car,
        CUSTOM_ENCRYPTION_HIERARCHY,
    )
    assert car.name == b"Secret Antique"
    key = content.encrypt()
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


def test_encryption_hierarchy_works_after_new_init():
    car = CarWithSecretName(name="Secret Antique")
    content = Content(
        "My Car",
        car,
        SYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    key = content.encrypt()

    content = Content(
        "My Car", car, CUSTOM_ENCRYPTION_HIERARCHY, content.encryption_version
    )
    content.decrypt(key)

    assert isinstance(car.name, OpenBox)
    assert car.name == b"Secret Antique"

    content.encrypt()

    assert content.encryption_version == 2
    assert b"Secret Antique" in SymmetricEncryptionTest2.get_treasure_chest().values()
    assert (
        b"Secret Antique" not in SymmetricEncryptionTest1.get_treasure_chest().values()
    )


def test_content_after_encryption():
    car = CarWithSecretName(name="Secret Antique")
    content = Content(
        "My Car",
        car,
        SYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    key = content.encrypt()

    car2 = CarWithSecretName(enc_name=car.name)
    content = Content(
        "My Car", car2, CUSTOM_ENCRYPTION_HIERARCHY, content.encryption_version
    )
    content.decrypt(key)

    assert car2.name == b"Secret Antique"
