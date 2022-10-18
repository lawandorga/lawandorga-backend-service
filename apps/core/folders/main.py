from typing import Literal, Optional, Type
from uuid import uuid4

from apps.core.folders.domain.aggregates.content import Content
from apps.core.folders.domain.aggregates.folder import Folder
from apps.core.folders.domain.aggregates.object import EncryptedObject
from apps.core.folders.domain.value_objects.box import OpenBox
from apps.core.folders.domain.value_objects.encryption import SymmetricEncryption
from apps.core.folders.domain.value_objects.key import (
    ContentKey,
    FolderKey,
    PasswordKey,
    SymmetricKey,
)
from apps.core.folders.infrastructure.asymmetric_encryptions import (
    AsymmetricEncryptionV1,
)
from apps.core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


class CarWithSecretName(EncryptedObject):
    ENCRYPTED_FIELDS = ["name"]

    def __init__(self, enc_name: Optional[bytes] = None, name: Optional[str] = None):
        self.enc_name = enc_name
        self.name = bytes(name, 'utf-8')


SYMMETRIC_ENCRYPTION_HIERARCHY = {1: SymmetricEncryptionV1}
ASYMMETRIC_ENCRYPTION_HIERARCHY = {1: AsymmetricEncryptionV1}


def test_1():
    _key = PasswordKey("test")

    _user = uuid4()

    _private_key, _public_key = AsymmetricEncryptionV1.generate_keys()
    _folder_key = FolderKey(_user, _private_key, _public_key)

    _folder = Folder(
        "My Folder",
        encryption_class=AsymmetricEncryptionV1,
        keys=[_folder_key],
        public_key=_public_key,
    )

    _car = CarWithSecretName(name="BMW")

    _content = Content("My Car", _folder, _car, SYMMETRIC_ENCRYPTION_HIERARCHY, ASYMMETRIC_ENCRYPTION_HIERARCHY)

    _content.encrypt()

    print(_content.key)
    print(_car.enc_name)
    print(_car.name)

    print("#########")

    _content.decrypt(_folder_key)

    print(_content.key)
    print(_car.enc_name)
    print(_car.name)
