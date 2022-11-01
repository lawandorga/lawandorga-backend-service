import abc
from typing import Literal, Optional, Type, Union

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    EncryptionPyramid,
    SymmetricEncryption,
)


class Key(abc.ABC):
    KEY_TYPE: Literal["SYMMETRIC", "ASYMMETRIC"]
    _origin: str

    def __init__(self):
        assert self._origin is not None
        assert self.KEY_TYPE is not None

    @property
    def origin(self):
        return self._origin

    @abc.abstractmethod
    def get_encryption(self) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        pass

    def lock(self, box: OpenBox) -> LockedBox:
        return box.encrypt(self)

    def unlock(self, box: LockedBox) -> OpenBox:
        return box.decrypt(self)


class AsymmetricKey(Key):
    KEY_TYPE: Literal["ASYMMETRIC"] = "ASYMMETRIC"

    @abc.abstractmethod
    def get_decryption_key(self) -> Optional[str]:
        pass

    @abc.abstractmethod
    def get_encryption_key(self) -> str:
        pass

    def get_encryption(self) -> AsymmetricEncryption:
        encryption_class = EncryptionPyramid.get_encryption_class(self.origin)
        return encryption_class(
            public_key=self.get_encryption_key(), private_key=self.get_decryption_key()
        )

    def get_encryption_class(self) -> Type[AsymmetricEncryption]:
        hierarchy = EncryptionPyramid.get_asymmetric_encryption_hierarchy()
        return hierarchy[self._origin]


class SymmetricKey(Key):
    KEY_TYPE: Literal["SYMMETRIC"] = "SYMMETRIC"

    @abc.abstractmethod
    def get_key(self) -> str:
        pass

    def get_encryption(self) -> SymmetricEncryption:
        encryption_class = EncryptionPyramid.get_encryption_class(self.origin)
        return encryption_class(key=self.get_key())

    def get_encryption_class(self) -> Type[SymmetricEncryption]:
        hierarchy = EncryptionPyramid.get_symmetric_encryption_hierarchy()
        return hierarchy[self._origin]
