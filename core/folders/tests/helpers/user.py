from typing import Union
from uuid import uuid4

from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.keys import AsymmetricKey, SymmetricKey, EncryptedAsymmetricKey


class UserObject(IOwner):
    def __init__(self):
        self.slug = uuid4()
        self.key = AsymmetricKey.generate()

    def get_key(self):
        return self.key

    def get_decryption_key(self, *args, **kwargs) -> Union["AsymmetricKey", "SymmetricKey"]:
        return self.key

    def get_encryption_key(self, *args, **kwargs) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        return self.key
