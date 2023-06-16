from typing import TYPE_CHECKING, Optional, Union

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    EncryptionWarehouse,
    SymmetricEncryption,
)
from core.folders.domain.value_objects.key import Key

from seedwork.types import JsonDict

if TYPE_CHECKING:
    from core.folders.domain.value_objects.asymmetric_key import (
        AsymmetricKey,
        EncryptedAsymmetricKey,
    )


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


class EncryptedSymmetricKey(Key):
    @staticmethod
    def create(
        original: Optional[SymmetricKey] = None,
        key: Optional[
            Union["AsymmetricKey", SymmetricKey, "EncryptedAsymmetricKey"]
        ] = None,
    ) -> "EncryptedSymmetricKey":
        assert original is not None and key is not None

        enc_key = key.lock(original.get_key())

        return EncryptedSymmetricKey(enc_key=enc_key, origin=original.origin)

    @staticmethod
    def create_from_dict(d: JsonDict):
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

    def as_dict(self) -> JsonDict:
        return {
            "enc_key": self.__enc_key.as_dict(),
            "origin": self.origin,
        }

    def __hash__(self):
        return hash("{}{}".format(self.origin, hash(self.__enc_key)))

    def decrypt(self, unlock_key: Union["AsymmetricKey", SymmetricKey]) -> SymmetricKey:
        key = unlock_key.unlock(self.__enc_key)
        return SymmetricKey(key=key, origin=self.origin)

    def unlock(self, box: LockedBox) -> OpenBox:
        raise ValueError("This key is encrypted and can not lock a box.")

    def lock(self, box: OpenBox) -> LockedBox:
        raise ValueError("This key is encrypted and can not lock a box.")

    def get_encryption(self) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        raise ValueError("This key is encrypted and can not deliver a encryption.")
