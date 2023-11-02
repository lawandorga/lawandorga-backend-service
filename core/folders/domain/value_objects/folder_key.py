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


class EncryptedFolderKeyOfUser:
    TYPE = "FOLDER"

    @staticmethod
    def create_from_dict(d: JsonDict) -> "EncryptedFolderKeyOfUser":
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

        return EncryptedFolderKeyOfUser(
            key=key, owner_uuid=owner_uuid, is_valid=is_valid
        )

    def __init__(
        self,
        owner_uuid: UUID,
        key: EncryptedSymmetricKey,
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
    def owner_uuid(self) -> UUID:
        return self.__owner_uuid

    @property
    def is_valid(self):
        return self.__is_valid

    @property
    def is_encrypted(self):
        return True

    @property
    def key_origin(self):
        return self.__key.origin

    def invalidate_self(self) -> "EncryptedFolderKeyOfUser":
        return EncryptedFolderKeyOfUser(
            owner_uuid=self.__owner_uuid, key=self.__key, is_valid=False
        )

    def decrypt_self(self, user: "RlcUser") -> "FolderKeyOfUser":
        if not self.__is_valid:
            raise ValueError("This key is not valid.")

        assert isinstance(self.__key, EncryptedSymmetricKey)

        unlock_key = user.get_decryption_key()

        key = self.__key.decrypt(unlock_key)

        return FolderKeyOfUser(
            owner_uuid=self.__owner_uuid,
            key=key,
        )


class FolderKeyOfUser:
    def __init__(
        self,
        owner_uuid: UUID,
        key: SymmetricKey,
    ):
        super().__init__()

        assert owner_uuid is not None and key is not None

        self.__owner_uuid = owner_uuid
        self.__key = key

    def __str__(self):
        return "FolderKey of {}".format(self.__owner_uuid)

    def __repr__(self):
        return str(self)

    @property
    def key(self):
        return self.__key

    @property
    def owner_uuid(self) -> UUID:
        return self.__owner_uuid

    @property
    def is_valid(self):
        return True

    @property
    def is_encrypted(self):
        return True

    def encrypt_self(
        self, key: Union[AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey]
    ) -> "EncryptedFolderKeyOfUser":
        assert isinstance(self.__key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=self.__key, key=key)

        return EncryptedFolderKeyOfUser(
            owner_uuid=self.__owner_uuid,
            key=enc_key,
        )
