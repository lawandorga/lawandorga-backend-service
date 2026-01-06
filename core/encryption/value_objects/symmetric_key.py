from typing import TYPE_CHECKING, Any, Optional, Union

from core.encryption.encryptions import ENCRYPTIONS
from core.encryption.value_objects.box import LockedBox, OpenBox
from core.encryption.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)
from core.encryption.value_objects.key import Key

from seedwork.types import JsonDict

if TYPE_CHECKING:
    from core.encryption.value_objects.asymmetric_key import (
        AsymmetricKey,
        EncryptedAsymmetricKey,
    )


class SymmetricKey(Key):
    @staticmethod
    def generate(enc: type[SymmetricEncryption]) -> "SymmetricKey":
        (
            key,
            version,
        ) = enc.generate_key()
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
        encryption_class = ENCRYPTIONS[self.origin]
        assert issubclass(encryption_class, SymmetricEncryption)
        return encryption_class(key=self.get_key().decode("utf-8"))

    def encrypt_self(
        self, key: Union["SymmetricKey", "AsymmetricKey", "EncryptedAsymmetricKey"]
    ) -> "EncryptedSymmetricKey":
        return EncryptedSymmetricKey.create(original=self, key=key)


class EncryptedSymmetricKey(Key):
    @staticmethod
    def create(
        original: Optional[SymmetricKey] = None,
        key: Union[
            "AsymmetricKey", SymmetricKey, "EncryptedAsymmetricKey", None
        ] = None,
    ) -> "EncryptedSymmetricKey":
        assert original is not None and key is not None

        enc_key = key.lock(original.get_key())

        return EncryptedSymmetricKey(enc_key=enc_key, origin=original.origin)

    @staticmethod
    def create_from_dict(d: Any):
        assert isinstance(d, dict)
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
