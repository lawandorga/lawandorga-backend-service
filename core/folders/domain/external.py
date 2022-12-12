import abc
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from core.folders.domain.aggregates.folder import Folder
    from core.folders.domain.value_objects.asymmetric_key import (
        AsymmetricKey,
        EncryptedAsymmetricKey,
    )
    from core.folders.domain.value_objects.symmetric_key import SymmetricKey


class IOwner:
    uuid: Any
    has_invalid_keys: bool

    @abc.abstractmethod
    def get_encryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey", "EncryptedAsymmetricKey"]:
        pass

    @abc.abstractmethod
    def get_decryption_key(
        self, *args, **kwargs
    ) -> Union["AsymmetricKey", "SymmetricKey"]:
        pass

    def invalidate_keys(self, folders: list["Folder"]):
        for folder in folders:
            folder.invalidate_keys_of(self)

    def check_has_invalid_keys(self, folders: list["Folder"]):
        for folder in folders:
            if folder.has_invalid_keys(self):
                return True
        return False

    def fix_keys_of(self, someone_else: "IOwner", folders: list["Folder"]):
        for folder in folders:
            if folder.has_access(self) and folder.has_invalid_keys(someone_else):
                folder.fix_keys(someone_else, self)
