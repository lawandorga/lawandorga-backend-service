from typing import Union
from uuid import UUID, uuid4

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.symmetric_key import SymmetricKey


class UserObject(OrgUser):
    class Meta:
        abstract = True

    def __init__(self):
        self.uuid = uuid4()
        self.key = AsymmetricKey.generate()

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
            if folder.has_invalid_keys(self):
                return True
        return False

    def fix_keys_of(self, someone_else: "UserObject", folders: list["Folder"]):
        for folder in folders:
            if folder.has_access(self) and folder.has_invalid_keys(someone_else):
                folder.fix_keys(someone_else, self)


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
