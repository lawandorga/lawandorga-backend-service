from typing import Optional, Union

from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    EncryptionWarehouse,
)
from core.folders.domain.value_objects.key import Key
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)


class AsymmetricKey(Key):
    @staticmethod
    def generate() -> "AsymmetricKey":
        (
            private_key,
            public_key,
            version,
        ) = EncryptionWarehouse.get_highest_asymmetric_encryption().generate_keys()
        return AsymmetricKey.create(
            private_key=private_key, public_key=public_key, origin=version
        )

    @staticmethod
    def create(
        private_key: Optional[str] = None,
        origin: Optional[str] = None,
        public_key: Optional[str] = None,
    ) -> "AsymmetricKey":
        assert private_key is not None

        return AsymmetricKey(
            private_key=OpenBox(data=private_key.encode("utf-8")),
            origin=origin,
            public_key=public_key,
        )

    def __init__(
        self,
        private_key: Optional[OpenBox] = None,
        public_key: Optional[str] = None,
        origin: Optional[str] = None,
    ):
        assert private_key is not None and public_key is not None and origin is not None

        self.__public_key = public_key
        self.__private_key = private_key

        super().__init__(origin)

    def __hash__(self):
        return hash(
            "{}{}{}".format(self.origin, hash(self.__private_key), self.__public_key)
        )

    def get_encryption(self) -> AsymmetricEncryption:
        encryption_class = EncryptionWarehouse.get_encryption_class(self.origin)
        return encryption_class(
            public_key=self.__public_key, private_key=self.__private_key.decode("utf-8")
        )

    def get_private_key(self) -> OpenBox:
        return self.__private_key

    def get_public_key(self) -> str:
        return self.__public_key


class EncryptedAsymmetricKey(Key):
    @staticmethod
    def create(
        original: Optional[AsymmetricKey] = None,
        key: Optional[
            Union[AsymmetricKey, "EncryptedAsymmetricKey", SymmetricKey]
        ] = None,
    ) -> "EncryptedAsymmetricKey":
        assert (
            original is not None
            and key is not None
            and (
                isinstance(key, AsymmetricKey)
                or isinstance(key, EncryptedAsymmetricKey)
                or isinstance(key, SymmetricKey)
            )
        )

        s_key = SymmetricKey.generate()
        enc_private_key = s_key.lock(original.get_private_key())
        enc_s_key = EncryptedSymmetricKey.create(s_key, key)

        return EncryptedAsymmetricKey(
            enc_key=enc_s_key,
            enc_private_key=enc_private_key,
            public_key=original.get_public_key(),
            origin=original.origin,
        )

    @staticmethod
    def create_from_dict(d: StrDict):
        assert (
            "enc_private_key" in d
            and "public_key" in d
            and "origin" in d
            and isinstance(d["enc_private_key"], dict)
            and isinstance(d["public_key"], str)
            and isinstance(d["origin"], str)
        )
        assert ("enc_key" in d and isinstance(d["enc_key"], dict)) or "enc_key" not in d

        enc_s_key: Optional[EncryptedSymmetricKey] = None
        if "enc_key" in d and isinstance(d["enc_key"], dict):
            enc_s_key = EncryptedSymmetricKey.create_from_dict(d["enc_key"])

        enc_private_key = LockedBox.create_from_dict(d["enc_private_key"])
        public_key = d["public_key"]
        origin = d["origin"]

        return EncryptedAsymmetricKey(
            enc_key=enc_s_key,
            enc_private_key=enc_private_key,
            public_key=public_key,
            origin=origin,
        )

    def __init__(
        self,
        enc_key: Optional[EncryptedSymmetricKey] = None,
        enc_private_key: Optional[LockedBox] = None,
        public_key: Optional[str] = None,
        origin: Optional[str] = None,
    ):
        assert public_key is not None

        self.__enc_key = enc_key
        self.__enc_private_key = enc_private_key
        self.__public_key = public_key

        super().__init__(origin=origin)

    def as_dict(self) -> StrDict:
        if self.__enc_private_key is None:
            raise ValueError("The private key of this key is of type 'None'.")

        data = {
            "enc_private_key": self.__enc_private_key.as_dict(),
            "public_key": self.__public_key,
            "origin": self.origin,
        }

        if self.__enc_key:
            data["enc_key"] = self.__enc_key.as_dict()

        return data

    def __hash__(self):
        return hash(
            "{}{}{}{}".format(
                hash(self.__enc_key),
                hash(self.__enc_private_key),
                self.__public_key,
                self.origin,
            )
        )

    def get_encryption(self) -> AsymmetricEncryption:
        encryption_class = EncryptionWarehouse.get_encryption_class(self.origin)
        return encryption_class(public_key=self.__public_key)

    def unlock(self, box: LockedBox) -> OpenBox:
        raise ValueError("This key is encrypted and can not unlock a box.")

    def decrypt(self, unlock_key: Union[AsymmetricKey, SymmetricKey]) -> AsymmetricKey:
        if self.__enc_private_key is None:
            raise ValueError("The private key of this key is of type 'None'.")

        s_key = self.__enc_key.decrypt(unlock_key) if self.__enc_key else unlock_key

        private_key = s_key.unlock(self.__enc_private_key)

        return AsymmetricKey(
            private_key=private_key, public_key=self.__public_key, origin=self.origin
        )

    def get_public_key(self) -> str:
        return self.__public_key
