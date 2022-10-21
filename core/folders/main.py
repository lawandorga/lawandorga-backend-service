# type: ignore
# flake8: noqa
from typing import Optional
from uuid import uuid4

from core.folders.domain.aggregates.content import Content
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.object import EncryptedObject
from core.folders.domain.value_objects.key import FolderKey, PasswordKey
from core.folders.infrastructure.asymmetric_encryptions import AsymmetricEncryptionV1
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1


class CarWithSecretName(EncryptedObject):
    ENCRYPTED_FIELDS = ["name"]

    def __init__(self, enc_name: Optional[bytes] = None, name: Optional[str] = None):
        if isinstance(name, str):
            self.name = bytes(name, "utf-8")
        if isinstance(enc_name, bytes):
            self.name = enc_name


SYMMETRIC_ENCRYPTION_HIERARCHY = {1: SymmetricEncryptionV1}
ASYMMETRIC_ENCRYPTION_HIERARCHY = {1: AsymmetricEncryptionV1}


def f1():
    key = PasswordKey("test")

    user = uuid4()

    private_key, public_key = AsymmetricEncryptionV1.generate_keys()
    folder_key = FolderKey(user, private_key, public_key)

    folder = Folder(
        "My Folder",
        asymmetric_encryption_hierarchy=ASYMMETRIC_ENCRYPTION_HIERARCHY,
    )

    # secret car
    car = CarWithSecretName(name="BMW")
    content = Content(
        "My Car",
        car,
        SYMMETRIC_ENCRYPTION_HIERARCHY,
    )
    key = content.encrypt()

    # add to folder
    folder.add_content(content, key, folder_key)

    # get content
    content = folder.get_content_by_name(content.name)
    content_key = folder.get_content_key(content, folder_key)
    content.decrypt(content_key)
    car = content.item

    print(car.name)


f1()
