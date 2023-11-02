from typing import TYPE_CHECKING, Union
from uuid import UUID

from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)

from seedwork.types import JsonDict

if TYPE_CHECKING:
    from core.auth.models.org_user import RlcUser


class FolderKey:
    TYPE = "FOLDER"

    @staticmethod
    def create_from_dict(d: JsonDict) -> "FolderKey":
        assert (
            "key" in d
            and isinstance(d["key"], dict)
            and "owner" in d
            and isinstance(d["owner"], str)
            and "type" in d
            and d["type"] == "FOLDER"
        )

        key = EncryptedSymmetricKey.create_from_dict(d["key"])
        owner_uuid = UUID(d["owner"])

        is_valid: bool = True
        if "is_valid" in d:
            assert isinstance(d["is_valid"], bool)
            is_valid = d["is_valid"]

        return FolderKey(key=key, owner_uuid=owner_uuid, is_valid=is_valid)

    def __init__(
        self,
        owner_uuid: UUID,
        key: Union[SymmetricKey, EncryptedSymmetricKey],
        is_valid: bool = True,
    ):
        assert owner_uuid is not None and key is not None

        self.__is_valid = is_valid
        self.__owner_uuid = owner_uuid
        self.__key = key

        super().__init__()

    def __str__(self):
        return "FolderKey of {}".format(self.__owner_uuid)

    def __repr__(self):
        return str(self)

    def as_dict(self) -> JsonDict:
        assert isinstance(self.__key, EncryptedSymmetricKey)

        data: JsonDict = {
            "owner": str(self.__owner_uuid),
            "key": self.__key.as_dict(),
            "type": self.TYPE,
            "is_valid": self.__is_valid,
        }

        return data

    @property
    def key(self):
        return self.__key

    @property
    def owner_uuid(self) -> UUID:
        return self.__owner_uuid

    @property
    def is_valid(self):
        return self.__is_valid

    @property
    def is_encrypted(self):
        return isinstance(self.__key, EncryptedSymmetricKey)

    def invalidate_self(self) -> "FolderKey":
        return FolderKey(owner_uuid=self.__owner_uuid, key=self.__key, is_valid=False)

    def encrypt_self(
        self, key: Union[AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey]
    ) -> "FolderKey":
        if not self.__is_valid:
            raise ValueError("This key is not valid.")

        assert isinstance(self.__key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=self.__key, key=key)

        return FolderKey(
            owner_uuid=self.__owner_uuid,
            key=enc_key,
        )

    def decrypt_self(self, user: "RlcUser") -> "FolderKey":
        if not self.__is_valid:
            raise ValueError("This key is not valid.")

        assert isinstance(self.__key, EncryptedSymmetricKey)

        unlock_key = user.get_decryption_key()

        key = self.__key.decrypt(unlock_key)

        return FolderKey(
            owner_uuid=self.__owner_uuid,
            key=key,
        )
