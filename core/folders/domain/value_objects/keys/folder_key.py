from typing import Optional, Union

from core.folders.domain.external import IOwner
from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.keys import AsymmetricKey
from core.folders.domain.value_objects.keys.base import (
    EncryptedAsymmetricKey,
    EncryptedSymmetricKey,
    SymmetricKey,
)


class FolderKey:
    @staticmethod
    def create_from_dict(d: StrDict, owner: IOwner) -> "FolderKey":
        assert (
            "key" in d
            and isinstance(d["key"], dict)
            and "owner" in d
            and isinstance(d["owner"], str)
            and "type" in d
            and d["type"] == "FOLDER"
        )

        key = EncryptedSymmetricKey.create_from_dict(d["key"])
        assert str(owner.slug) == d["owner"]

        return FolderKey(key=key, owner=owner)

    def __init__(
        self,
        owner: Optional[IOwner] = None,
        key: Optional[Union[SymmetricKey, EncryptedSymmetricKey]] = None,
    ):
        assert owner is not None and key is not None

        self.__owner = owner
        self.__key = key

        super().__init__()

    def __str__(self):
        return "FolderKey of {}".format(self.__owner.slug)

    def as_dict(self) -> StrDict:
        assert isinstance(self.__key, EncryptedSymmetricKey)

        return {
            "owner": str(self.__owner.slug),
            "key": self.__key.as_dict(),
            "type": "FOLDER",
        }

    @property
    def key(self):
        return self.__key

    @property
    def owner(self):
        return self.__owner

    @property
    def is_encrypted(self):
        return isinstance(self.__key, EncryptedSymmetricKey)

    def encrypt_self(
        self, key: Union[AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey]
    ) -> "FolderKey":
        assert isinstance(self.__key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=self.__key, key=key)

        return FolderKey(
            owner=self.__owner,
            key=enc_key,
        )

    def decrypt_self(self, user: IOwner) -> "FolderKey":
        assert isinstance(self.__key, EncryptedSymmetricKey)

        unlock_key = self.__owner.get_decryption_key(requestor=user)

        key = self.key.decrypt(unlock_key)

        return FolderKey(
            owner=self.__owner,
            key=key,
        )
