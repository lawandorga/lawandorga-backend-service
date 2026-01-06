from core.encryption.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.encryption.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.folders.tests.test_helpers.encryptions import (
    AsymmetricEncryptionTest1,
    AsymmetricEncryptionTest2,
    SymmetricEncryptionTest1,
    SymmetricEncryptionTest2,
)

ENCRYPTIONS = {
    # prod
    AsymmetricEncryptionV1.VERSION: AsymmetricEncryptionV1,
    SymmetricEncryptionV1.VERSION: SymmetricEncryptionV1,
    # test
    AsymmetricEncryptionTest1.VERSION: AsymmetricEncryptionTest1,
    AsymmetricEncryptionTest2.VERSION: AsymmetricEncryptionTest2,
    SymmetricEncryptionTest1.VERSION: SymmetricEncryptionTest1,
    SymmetricEncryptionTest2.VERSION: SymmetricEncryptionTest2,
}
