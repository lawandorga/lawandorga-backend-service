from core.collab.value_objects.document import Document
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


def test_document_encrypt_and_decrypt():
    key = SymmetricKey.generate(SymmetricEncryptionV1)
    document = Document.create(text="hello world", user="alice")
    encrypted_document = document.encrypt(key)
    assert encrypted_document._user == "alice"
    assert encrypted_document._enc_text != "hello world"
    loaded = encrypted_document.decrypt(key)
    assert loaded._text == "hello world"
    assert loaded._user == "alice"
