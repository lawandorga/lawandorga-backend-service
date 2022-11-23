from typing import Optional, Union
from uuid import UUID

from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.keys.base import (
    EncryptedSymmetricKey,
    SymmetricKey,
)


class ParentKey:
    @staticmethod
    def create_from_dict(d: StrDict) -> "ParentKey":
        assert (
            "key" in d
            and isinstance(d["key"], dict)
            and "folder_pk" in d
            and isinstance(d["folder_pk"], str)
            and "type" in d
            and d["type"] == "PARENT"
        )

        key = EncryptedSymmetricKey.create_from_dict(d["key"])
        folder_pk = UUID(d["folder_pk"])

        return ParentKey(key=key, folder_pk=folder_pk)

    def __init__(
        self,
        folder_pk: Optional[UUID] = None,
        key: Optional[Union[SymmetricKey, EncryptedSymmetricKey]] = None,
    ):
        assert folder_pk is not None and key is not None

        self.__folder_pk = folder_pk
        self.__key = key

    def __str__(self):
        return "ParentKey of {}".format(self.__folder_pk)

    def as_dict(self) -> StrDict:
        assert isinstance(self.__key, EncryptedSymmetricKey)

        return {
            "folder_pk": str(self.__folder_pk),
            "key": self.__key.as_dict(),
            "type": "PARENT",
        }

    @property
    def key(self) -> Union[EncryptedSymmetricKey, SymmetricKey]:
        return self.__key

    @property
    def folder_pk(self):
        return self.__folder_pk

    @property
    def is_encrypted(self):
        return isinstance(self.__key, EncryptedSymmetricKey)

    def encrypt_self(self, key: SymmetricKey) -> "ParentKey":
        assert isinstance(self.__key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=self.__key, key=key)

        return ParentKey(
            folder_pk=self.__folder_pk,
            key=enc_key,
        )

    def decrypt_self(self, key: SymmetricKey) -> "ParentKey":
        assert isinstance(self.__key, EncryptedSymmetricKey)

        dec_key = self.__key.decrypt(key)

        return ParentKey(
            folder_pk=self.__folder_pk,
            key=dec_key,
        )
