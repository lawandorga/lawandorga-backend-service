from typing import Union

from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.symmetric_key import SymmetricKey

from seedwork.types import JsonDict


class UserKey:
    @staticmethod
    def create_from_unsafe_dict(d: JsonDict) -> "UserKey":
        assert "type" in d and d["type"] == "USER_UNSAFE"
        assert (
            "private_key" in d
            and "public_key" in d
            and "origin" in d
            and isinstance(d["private_key"], str)
            and isinstance(d["public_key"], str)
            and isinstance(d["origin"], str)
        )

        key = AsymmetricKey.create(
            private_key=d["private_key"],
            public_key=d["public_key"],
            origin=d["origin"],
        )

        return UserKey(key)

    @staticmethod
    def create_from_dict(d: JsonDict) -> "UserKey":
        assert "type" in d and d["type"] == "USER"
        assert ("key" in d and isinstance(d["key"], dict)) or (
            "private_key" in d
            and "public_key" in d
            and "origin" in d
            and isinstance(d["private_key"], str)
            and isinstance(d["public_key"], str)
            and isinstance(d["origin"], str)
        )

        if "key" in d:
            assert isinstance(d["key"], dict)
            key = EncryptedAsymmetricKey.create_from_dict(d["key"])
            return UserKey(key)
        else:
            assert (
                isinstance(d["private_key"], str)
                and isinstance(d["public_key"], str)
                and isinstance(d["origin"], str)
            )
            key = AsymmetricKey.create(
                private_key=d["private_key"],
                public_key=d["public_key"],
                origin=d["origin"],
            )
            return UserKey(key)

    def __init__(
        self,
        key: Union[AsymmetricKey, EncryptedAsymmetricKey],
    ):
        self.__key = key
        super().__init__()

    def __str__(self):
        return "UserKey"

    def __eq__(self, other):
        if isinstance(other, UserKey):
            return hash(self) == hash(other)
        return False

    def __hash__(self):
        return hash(self.__key)

    def as_dict(self) -> JsonDict:
        assert isinstance(self.__key, EncryptedAsymmetricKey)

        return {
            "key": self.__key.as_dict(),
            "type": "USER",
        }

    def as_unsafe_dict(self) -> JsonDict:
        assert isinstance(self.__key, AsymmetricKey)

        return {
            "type": "USER_UNSAFE",
            "private_key": self.__key.get_private_key().decode("utf-8"),
            "public_key": self.__key.get_public_key(),
            "origin": self.__key.origin,
        }

    @property
    def key(self) -> Union[EncryptedAsymmetricKey, AsymmetricKey]:
        return self.__key

    @property
    def is_encrypted(self):
        return isinstance(self.__key, EncryptedAsymmetricKey)

    def encrypt_self(self, password: str) -> "UserKey":
        assert isinstance(self.__key, AsymmetricKey)

        key = SymmetricKey(key=OpenBox(data=password.encode("utf-8")), origin="S1")
        enc_key = EncryptedAsymmetricKey.create(original=self.__key, key=key)

        return UserKey(key=enc_key)

    def decrypt_self(self, password: str) -> "UserKey":
        assert isinstance(self.__key, EncryptedAsymmetricKey)

        unlock_key = SymmetricKey(
            key=OpenBox(data=password.encode("utf-8")), origin="S1"
        )
        key = self.__key.decrypt(unlock_key)

        return UserKey(key=key)
