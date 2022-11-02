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

    def __init__(self, origin: str):
        self.__origin = origin
        assert self.__origin is not None
        assert self.KEY_TYPE is not None

    @property
    def origin(self):
        return self.__origin

    @abc.abstractmethod
    def get_encryption(self) -> Union[SymmetricEncryption, AsymmetricEncryption]:
        pass

    def lock(self, box: OpenBox) -> LockedBox:
        encryption = self.get_encryption()
        enc_data = encryption.encrypt(box.value)
        return LockedBox(enc_data=enc_data, encryption_version=self.origin)

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
    KEY_TYPE: Literal["SYMMETRIC"] = "SYMMETRIC"

    @staticmethod
    def create(key: str, origin: str) -> "SymmetricKey":
        return SymmetricKey(key=OpenBox(data=key.encode("utf-8")), origin=origin)

    def __init__(
        self,
        key: Union[OpenBox, LockedBox] = None,
        origin: Optional[str] = None,
    ):
        assert origin is not None

        self.__key = key

        super().__init__(origin)

    def get_key(self) -> str:
        assert isinstance(self.__key, OpenBox)
        key = self.__key.decode("utf-8")
        return key

    def get_encryption(self) -> SymmetricEncryption:
        encryption_class = EncryptionPyramid.get_encryption_class(self.origin)
        return encryption_class(key=self.get_key())

    def get_encryption_class(self) -> Type[SymmetricEncryption]:
        hierarchy = EncryptionPyramid.get_symmetric_encryption_hierarchy()
        return hierarchy[self.origin]


class AsymmetricKey(Key):
    KEY_TYPE: Literal["ASYMMETRIC"] = "ASYMMETRIC"

    @staticmethod
    def create(
        private_key: str = None,
        origin: str = None,
        public_key: str = None,
    ) -> "AsymmetricKey":
        assert private_key is not None

        return AsymmetricKey(
            private_key=OpenBox(data=private_key.encode("utf-8")),
            origin=origin,
            public_key=public_key,
        )

    def __init__(
        self,
        private_key: Union[LockedBox, OpenBox] = None,
        public_key: str = None,
        origin: str = None,
    ):
        assert private_key is not None and public_key is not None and origin is not None

        self.__public_key = public_key
        self.__private_key = private_key

        super().__init__(origin)

    def get_encryption(self) -> AsymmetricEncryption:
        encryption_class = EncryptionPyramid.get_encryption_class(self.origin)
        return encryption_class(
            public_key=self.__public_key, private_key=self.__private_key
        )

    def get_encryption_class(self) -> Type[AsymmetricEncryption]:
        hierarchy = EncryptionPyramid.get_asymmetric_encryption_hierarchy()
        return hierarchy[self.origin]
