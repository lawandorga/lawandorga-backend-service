from typing import Union
from uuid import uuid4

from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
    SymmetricKey,
)


class UserObject(IOwner):
    def __init__(self):
        self.uuid = uuid4()
        self.key = AsymmetricKey.generate()

    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]:
        return self.key

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        return self.key


class ForeignUserObject(IOwner):
    def __init__(self):
        self.uuid = uuid4()
        self.key = AsymmetricKey.generate()

    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]:
        raise ValueError("The key can not be decrypted.")

    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        return EncryptedAsymmetricKey(
            public_key=self.key.get_public_key(), origin=self.key.origin
        )
