from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    FolderKey,
    SymmetricKey,
)
from core.folders.domain.value_objects.keys.base import EncryptedSymmetricKey
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


def test_asymmetric_encryption():
    EncryptionPyramid.reset_encryption_hierarchies()
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionV1)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionV1)

    s_key = SymmetricKey.generate()

    a_key = AsymmetricKey.generate()
    folder_key = FolderKey(key=a_key, owner={})

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
    EncryptionPyramid.reset_encryption_hierarchies()
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionV1)

    key = AsymmetricKey.generate()
    data = OpenBox(data=b'Secret')
    locked = key.lock(data)

    assert locked.decode('ISO-8859-1').encode('ISO-8859-1') == locked.value
    locked.__dict__()
