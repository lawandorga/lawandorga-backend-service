import abc
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
    from core.auth.models.org_user import OrgUser
    from core.rlc.models.group import Group


class FolderKey(abc.ABC):
    def __init__(
        self,
        owner_uuid: UUID,
        key: SymmetricKey,
    ):
        super().__init__()

        assert owner_uuid is not None and key is not None

        self._owner_uuid = owner_uuid
        self._key = key

    def __str__(self):
        return "FolderKey of '{}'".format(self._owner_uuid)

    def __repr__(self):
        return str(self)

    @property
    def key(self):
        return self._key

    @property
    def owner_uuid(self) -> UUID:
        return self._owner_uuid

    @property
    def is_valid(self):
        return True

    @property
    def is_encrypted(self):
        return False


class EncryptedFolderKey(abc.ABC):
    TYPE = "FOLDER"

    @classmethod
    def create_from_dict(cls, d: JsonDict):
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

        return cls(key=key, owner_uuid=owner_uuid, is_valid=is_valid)

    def __init__(
        self,
        owner_uuid: UUID,
        key: EncryptedSymmetricKey,
        is_valid: bool = True,
    ):
        super().__init__()

        assert owner_uuid is not None and key is not None

        self._is_valid = is_valid
        self._owner_uuid = owner_uuid
        self._key = key

    def __repr__(self):
        return str(self)

    @property
    def owner_uuid(self) -> UUID:
        return self._owner_uuid

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def is_encrypted(self):
        return True

    @property
    def key_origin(self):
        return self._key.origin

    def as_dict(self) -> JsonDict:
        assert isinstance(self._key, EncryptedSymmetricKey)

        data: JsonDict = {
            "owner": str(self._owner_uuid),
            "key": self._key.as_dict(),
            "type": self.TYPE,
            "is_valid": self._is_valid,
        }

        return data

    def invalidate_self(self) -> "EncryptedFolderKey":
        raise NotImplementedError()


class EncryptedFolderKeyOfUser(EncryptedFolderKey):
    @classmethod
    def create_from_key(
        cls,
        key: FolderKey,
        lock_key: Union[AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey],
    ) -> "EncryptedFolderKeyOfUser":
        assert isinstance(key.key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=key.key, key=lock_key)

        return EncryptedFolderKeyOfUser(
            owner_uuid=key.owner_uuid,
            key=enc_key,
        )

    def __str__(self):
        return "EncryptedFolderKeyOfUser '{}'".format(self._owner_uuid)

    def decrypt_self(self, user: "OrgUser") -> "FolderKey":
        if not self._is_valid:
            raise ValueError("This key is not valid.")

        assert isinstance(self._key, EncryptedSymmetricKey)

        unlock_key = user.get_decryption_key()

        key = self._key.decrypt(unlock_key)

        return FolderKey(
            owner_uuid=self._owner_uuid,
            key=key,
        )

    def test(self, user: "OrgUser") -> bool:
        assert user.uuid == self._owner_uuid, "the owner does not match the key"
        assert user.get_decryption_key(), "owner decryption key can not be fetched"
        try:
            self.decrypt_self(user)
        except Exception:
            return False
        return True

    def invalidate_self(self) -> "EncryptedFolderKeyOfUser":
        return EncryptedFolderKeyOfUser(
            owner_uuid=self._owner_uuid, key=self._key, is_valid=False
        )


class EncryptedFolderKeyOfGroup(EncryptedFolderKey):
    @classmethod
    def create_from_key(
        cls,
        key: FolderKey,
        lock_key: Union[AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey],
    ) -> "EncryptedFolderKeyOfGroup":
        assert isinstance(key.key, SymmetricKey)

        enc_key = EncryptedSymmetricKey.create(original=key.key, key=lock_key)

        return EncryptedFolderKeyOfGroup(
            owner_uuid=key.owner_uuid,
            key=enc_key,
        )

    def __str__(self):
        return "EncryptedFolderKeyOfGroup '{}'".format(self._owner_uuid)

    def decrypt_self(self, group: "Group", user: "OrgUser") -> "FolderKey":
        if not self._is_valid:
            raise ValueError("This key is not valid.")

        assert isinstance(self._key, EncryptedSymmetricKey)

        unlock_key = group.get_decryption_key(user=user)

        key = self._key.decrypt(unlock_key)

        return FolderKey(
            owner_uuid=self._owner_uuid,
            key=key,
        )

    def invalidate_self(self) -> EncryptedFolderKey:
        raise ValueError("Group keys can not be invalidated.")
