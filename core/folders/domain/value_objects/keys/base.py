import abc
from typing import Optional, Union

from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    EncryptionWarehouse,
    SymmetricEncryption,
)


class Key(abc.ABC):
    def __init__(self, origin: Optional[str] = None):
        assert origin is not None

        self.__origin = origin

    def __eq__(self, other):
        if type(other) == type(self):
            return hash(other) == hash(self)
        return NotImplemented

    @property
    def origin(self):
        return self.__origin

    @abc.abstractmethod
    def get_encryption(self) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        pass

    def lock(self, box: OpenBox) -> LockedBox:
        encryption = self.get_encryption()
        enc_data = encryption.encrypt(box.value)
        return LockedBox(enc_data=enc_data, key_origin=self.origin)

    def unlock(self, box: LockedBox) -> OpenBox:
        if self.origin != box.key_origin:
            raise ValueError(
                "This key can not unlock this box because the encryption versions do not match. '{}' != '{}'.".format(
                    self.origin, box.key_origin
                )
            )
        encryption = self.get_encryption()
        data = encryption.decrypt(box.value)
        return OpenBox(data=data)


class SymmetricKey(Key):
    @staticmethod
    def generate() -> "SymmetricKey":
        (
            key,
            version,
        ) = EncryptionWarehouse.get_highest_symmetric_encryption().generate_key()
        return SymmetricKey.create(key, version)

    @staticmethod
    def create(key: str, origin: str) -> "SymmetricKey":
        return SymmetricKey(key=OpenBox(data=key.encode("utf-8")), origin=origin)

    def __init__(
        self,
        key: Optional[OpenBox] = None,
        origin: Optional[str] = None,
    ):
        assert origin is not None and key is not None

        self.__key = key

        super().__init__(origin)

    def __hash__(self):
        return hash("{}{}".format(self.origin, hash(self.__key)))

    def get_key(self) -> OpenBox:
        return self.__key

    def get_encryption(self) -> SymmetricEncryption:
        encryption_class = EncryptionWarehouse.get_encryption_class(self.origin)
        return encryption_class(key=self.get_key().decode("utf-8"))


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


class EncryptedSymmetricKey(Key):
    @staticmethod
    def create(
        original: Optional[SymmetricKey] = None,
        key: Optional[
            Union[AsymmetricKey, SymmetricKey, "EncryptedAsymmetricKey"]
        ] = None,
    ) -> "EncryptedSymmetricKey":
        assert original is not None and key is not None

        enc_key = key.lock(original.get_key())

        return EncryptedSymmetricKey(enc_key=enc_key, origin=original.origin)

    @staticmethod
    def create_from_dict(d: StrDict):
        assert (
            "enc_key" in d
            and "origin" in d
            and isinstance(d["enc_key"], dict)
            and isinstance(d["origin"], str)
        )

        enc_key = LockedBox.create_from_dict(d["enc_key"])
        origin = d["origin"]

        return EncryptedSymmetricKey(enc_key=enc_key, origin=origin)

    def __init__(
        self, enc_key: Optional[LockedBox] = None, origin: Optional[str] = None
    ):
        assert enc_key is not None

        self.__enc_key = enc_key

        super().__init__(origin=origin)

    def as_dict(self) -> StrDict:  # type: ignore
        return {
            "enc_key": self.__enc_key.as_dict(),
            "origin": self.origin,
        }

    def __hash__(self):
        return hash("{}{}".format(self.origin, hash(self.__enc_key)))

    def decrypt(self, unlock_key: Union[AsymmetricKey, SymmetricKey]) -> SymmetricKey:
        key = unlock_key.unlock(self.__enc_key)
        return SymmetricKey(key=key, origin=self.origin)

    def unlock(self, box: LockedBox) -> OpenBox:
        raise ValueError("This key is encrypted and can not lock a box.")

    def lock(self, box: OpenBox) -> LockedBox:
        raise ValueError("This key is encrypted and can not lock a box.")

    def get_encryption(self) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        raise ValueError("This key is encrypted and can not deliver a encryption.")


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
            "enc_key" in d
            and "enc_private_key" in d
            and "public_key" in d
            and "origin" in d
            and isinstance(d["enc_key"], dict)
            and isinstance(d["enc_private_key"], dict)
            and isinstance(d["public_key"], str)
            and isinstance(d["origin"], str)
        )

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

    def as_dict(self) -> StrDict:  # type: ignore
        if self.__enc_key is None or self.__enc_private_key is None:
            raise ValueError("One or more keys of this key are of type 'None'.")

        return {
            "enc_key": self.__enc_key.as_dict(),
            "enc_private_key": self.__enc_private_key.as_dict(),
            "public_key": self.__public_key,
            "origin": self.origin,
        }

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
        if self.__enc_key is None or self.__enc_private_key is None:
            raise ValueError(
                "This key can not be decrypted because one or more of its keys are of type 'None'."
            )

        s_key = self.__enc_key.decrypt(unlock_key)

        private_key = s_key.unlock(self.__enc_private_key)

        return AsymmetricKey(
            private_key=private_key, public_key=self.__public_key, origin=self.origin
        )
