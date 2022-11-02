from core.folders.domain.value_objects.encryption import EncryptionPyramid
from core.folders.domain.value_objects.keys import ContentKey, FolderKey
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


def test_asymmetric_encryption():
    EncryptionPyramid.reset_encryption_hierarchies()
    EncryptionPyramid.add_symmetric_encryption(SymmetricEncryptionV1)
    EncryptionPyramid.add_asymmetric_encryption(AsymmetricEncryptionV1)

    key, version1 = EncryptionPyramid.get_highest_symmetric_encryption().generate_key()
    content_key = ContentKey.create(key=key, origin=version1)

    (
        private,
        public,
        version2,
    ) = EncryptionPyramid.get_highest_asymmetric_encryption().generate_keys()

    folder_key = FolderKey.create(
        private_key=private, public_key=public, origin=version2, owner={}
    )

    enc_content_key = content_key.encrypt(folder_key)
    dec_content_key = enc_content_key.decrypt(folder_key)

    assert dec_content_key.get_key() == key


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

    b_private = private.encode("utf-8")

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
