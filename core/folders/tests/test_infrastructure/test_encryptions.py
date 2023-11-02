from uuid import uuid4
from core.folders.domain.value_objects.asymmetric_key import AsymmetricKey, SymmetricKey
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.folder_key import FolderKey
from core.folders.domain.value_objects.symmetric_key import EncryptedSymmetricKey
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


def test_asymmetric_encryption():
    EncryptionWarehouse.reset_encryption_hierarchies()
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)

    s_key = SymmetricKey.generate()

    a_key = AsymmetricKey.generate()
    folder_key = FolderKey(key=a_key, owner_uuid=uuid4())

    enc_content_key = EncryptedSymmetricKey.create(s_key, folder_key.key)
    dec_content_key = enc_content_key.decrypt(folder_key.key)

    assert dec_content_key.get_key() == s_key.get_key()


def test_asymmetric_encryption_raw():
    private, public, version = AsymmetricEncryptionV1.generate_keys()

    data = b"Secret Data"

    encryption = AsymmetricEncryptionV1(private, public)

    enc_data = encryption.encrypt(data)
    assert enc_data != b"Secret Data"
    dec_data = encryption.decrypt(enc_data)
    assert dec_data == b"Secret Data"


def test_asymmetric_encryption_encrypt_private_key():
    private, public, version = AsymmetricEncryptionV1.generate_keys()

    encryption = AsymmetricEncryptionV1(private, public)

    b_private = b"my secret diary"

    enc_data = encryption.encrypt(b_private)
    assert enc_data != b_private
    dec_data = encryption.decrypt(enc_data)
    assert dec_data == b_private


def test_asymmetric_encryption_encrypt_symmetric_key():
    key, _ = SymmetricEncryptionV1.generate_key()
    private, public, _ = AsymmetricEncryptionV1.generate_keys()

    encryption = AsymmetricEncryptionV1(private, public)

    b_key = key.encode("utf-8")

    enc_data = encryption.encrypt(b_key)
    assert enc_data != b_key
    dec_data = encryption.decrypt(enc_data)
    assert dec_data == b_key


def test_asymmetric_encryption_decode():
    EncryptionWarehouse.reset_encryption_hierarchies()
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)

    key = AsymmetricKey.generate()
    data = OpenBox(data=b"Secret")
    locked = key.lock(data)

    assert locked.decode("ISO-8859-1").encode("ISO-8859-1") == locked.value
    locked.as_dict()
    EncryptionWarehouse.add_asymmetric_encryption(AsymmetricEncryptionV1)
    EncryptionWarehouse.add_symmetric_encryption(SymmetricEncryptionV1)
