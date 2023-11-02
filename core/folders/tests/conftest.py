import pytest

from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.folders.tests.test_helpers.encryptions import (
    AsymmetricEncryptionTest1,
    SymmetricEncryptionTest1,
)


@pytest.fixture
def encryption_reset():
    EncryptionWarehouse.reset_encryption_hierarchies()
    yield
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)


@pytest.fixture
def single_encryption(encryption_reset):
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionTest1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionTest1)
    yield
