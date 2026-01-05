from typing import Union
from uuid import UUID, uuid4

from core.auth.domain.user_key import UserKey
from core.encryption.models import Keyring
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.folders.tests.test_helpers.encryptions import AsymmetricEncryptionTest1


class UserObject:
    class Meta:
        abstract = True

    def __init__(self):
        self.uuid = uuid4()
        self.key = AsymmetricKey.generate(enc=AsymmetricEncryptionTest1)
        user_key = UserKey(key=self.key)
        user_key_enc = user_key.encrypt_self("qwe213")
        self.keyring = Keyring.create(
            user=None,
            key=user_key_enc,
        )
        self.keyring.decryption_key = self.key

    def __str__(self):
        return "UserObject"

    @property
    def groups(self):
        class Fake:
            def all(self):
                return []

        return Fake()

    def get_group_uuids(self) -> list[UUID]:
        return []

    def get_decryption_key(self, *args, **kwargs) -> "AsymmetricKey":
        return self.key

    def get_encryption_key(self, *args, **kwargs) -> "AsymmetricKey":
        return self.key

    def check_has_invalid_keys(self, folders: list["Folder"]):
        for folder in folders:
            if folder.has_invalid_keys(self):  # type: ignore
                return True
        return False

    def fix_keys_of(self, someone_else: "UserObject", folders: list["Folder"]):
        for folder in folders:
            if folder.has_access(self) and folder.has_invalid_keys(someone_else):  # type: ignore
                folder.fix_keys(someone_else, self)  # type: ignore


class ForeignUserObject(IOwner):
    def __init__(self):
        self.uuid = uuid4()
        self.key = AsymmetricKey.generate(enc=AsymmetricEncryptionTest1)

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
