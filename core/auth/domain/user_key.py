from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.keys.base import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
    SymmetricKey,
)


class UserKey:
    @staticmethod
    def create_from_dict(d: StrDict) -> "UserKey":
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
        key: EncryptedAsymmetricKey,
    ):
        self.__key = key
        super().__init__()

    def __str__(self):
        return "UserKey"

    def as_dict(self) -> StrDict:
        assert isinstance(self.__key, EncryptedAsymmetricKey)

        return {
            "key": self.__key.__dict__(),
            "type": "USER",
        }

    @property
    def key(self):
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
        key = self.key.decrypt(unlock_key)

        return UserKey(key=key)
