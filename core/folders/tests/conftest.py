import pytest

from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.tests.helpers.encryptions import (
    AsymmetricEncryptionTest1,
    AsymmetricEncryptionTest2,
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)

# from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
# from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


@pytest.fixture
def encryption_reset():
    EncryptionWarehouse.reset_encryption_hierarchies()
    yield


@pytest.fixture
def single_encryption(encryption_reset):
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    yield


@pytest.fixture
def double_encryption(encryption_reset):
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest2)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest2)
    yield
