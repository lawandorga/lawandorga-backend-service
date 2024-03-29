from typing import Optional, Union
from uuid import UUID

from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)

from seedwork.types import JsonDict


class ParentKey:
    TYPE = "PARENT"

    @staticmethod
    def create_from_dict(d: JsonDict) -> "ParentKey":
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

        return ParentKey(key=key, folder_uuid=folder_pk)

    def __init__(
        self,
        folder_uuid: Optional[UUID] = None,
        key: Optional[Union[SymmetricKey, EncryptedSymmetricKey]] = None,
    ):
        assert folder_uuid is not None and key is not None

        self.__folder_uuid = folder_uuid
        self.__key = key

    def __str__(self):
        return "ParentKey of {}".format(self.__folder_uuid)

    def as_dict(self) -> JsonDict:
        assert isinstance(self.__key, EncryptedSymmetricKey)

        return {
            "folder_pk": str(self.__folder_uuid),
            "key": self.__key.as_dict(),
            "type": "PARENT",
        }

    @property
    def key(self) -> Union[EncryptedSymmetricKey, SymmetricKey]:
        return self.__key

    @property
    def folder_pk(self):
        return self.__folder_uuid

    @property
    def is_encrypted(self):
        return isinstance(self.__key, EncryptedSymmetricKey)

    def encrypt_self(self, key: SymmetricKey) -> "ParentKey":
        assert isinstance(self.__key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=self.__key, key=key)

        return ParentKey(
            folder_uuid=self.__folder_uuid,
            key=enc_key,
        )

    def decrypt_self(self, key: SymmetricKey) -> "ParentKey":
        assert isinstance(self.__key, EncryptedSymmetricKey)

        dec_key = self.__key.decrypt(key)

        return ParentKey(
            folder_uuid=self.__folder_uuid,
            key=dec_key,
        )
