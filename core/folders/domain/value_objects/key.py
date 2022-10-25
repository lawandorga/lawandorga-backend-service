import abc
from typing import Literal, Optional, Type, Union
from uuid import UUID

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption, EncryptionPyramid,
)


class Key(abc.ABC):
    KEY_TYPE: Literal["SYMMETRIC", "ASYMMETRIC"]
    _encryption_version: str

    def __init__(self):
        assert self._encryption_version is not None
        assert self.KEY_TYPE is not None

    @property
    def encryption_version(self):
        return self._encryption_version

    def lock(self, box: OpenBox) -> LockedBox:
        return box.encrypt(self)

    def unlock(self, box: LockedBox) -> OpenBox:
        return box.decrypt(self)


class AsymmetricKey(Key):
    KEY_TYPE: Literal["ASYMMETRIC"] = "ASYMMETRIC"

    @abc.abstractmethod
    def get_decryption_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_encryption_key(self) -> str:
        pass

    def get_encryption(self) -> AsymmetricEncryption:
        encryption_class = EncryptionPyramid.get_encryption_class(self.encryption_version)
        return encryption_class(
            public_key=self.get_encryption_key(), private_key=self.get_decryption_key()
        )

    def get_encryption_class(self) -> Type[AsymmetricEncryption]:
        hierarchy = EncryptionPyramid.get_asymmetric_encryption_hierarchy()
        return hierarchy[self._encryption_version]


class SymmetricKey(Key):
    KEY_TYPE: Literal["SYMMETRIC"] = "SYMMETRIC"

    @abc.abstractmethod
    def get_key(self) -> str:
        pass

    def get_encryption(self) -> AsymmetricEncryption:
        encryption_class = EncryptionPyramid.get_encryption_class(self.encryption_version)
        return encryption_class(key=self.get_key())

    def get_encryption_class(self) -> Type[SymmetricEncryption]:
        hierarchy = EncryptionPyramid.get_symmetric_encryption_hierarchy()
        return hierarchy[self._encryption_version]


class Owner(abc.ABC):
    slug: UUID

    @abc.abstractmethod
    def get_key(self) -> AsymmetricKey:
        pass


class FolderKey(AsymmetricKey):
    __private_key: Union[OpenBox, LockedBox]

    def __init__(
        self,
        owner: Optional[Owner] = None,
        folder_pk: Optional[UUID] = None,
        private_key: Optional[str] = None,
        enc_private_key: Optional[bytes] = None,
        public_key: Optional[str] = None,
        encryption_version: str = None,
    ):
        assert owner is not None and encryption_version is not None

        self.__folder_pk = folder_pk
        self.__owner = owner
        self.__public_key = public_key
        self._encryption_version = encryption_version

        if private_key:
            assert private_key is not None
            bytes_key = private_key.encode("utf-8")
            self.__private_key = OpenBox(data=bytes_key)

        elif enc_private_key:
            assert enc_private_key is not None
            encryption_class = self.get_encryption_class()
            self.__private_key = LockedBox(
                enc_data=enc_private_key, encryption_class=encryption_class
            )

        super().__init__()

    def encrypt(self, encryption_class: Type[AsymmetricEncryption]) -> "FolderKey":
        assert isinstance(self.__private_key, OpenBox)

        lock_key = self.__owner.get_key()
        enc_key = self.__private_key.lock(lock_key, encryption_class)
        return FolderKey(
            enc_private_key=enc_key,
            encryption_class=encryption_class,
            public_key=self.__public_key,
        )

    def decrypt(self) -> "FolderKey":
        assert isinstance(self.__private_key, LockedBox)

        unlock_key = self.__owner.get_key()
        bytes_key = self.__private_key.unlock(unlock_key)
        key = bytes_key.decode("utf-8")
        return FolderKey(private_key=key, public_key=self.__public_key)

    def get_encryption_key(self) -> str:
        assert self.__public_key is not None
        return self.__public_key

    def get_decryption_key(self) -> str:
        assert self.__private_key is not None
        return self.__private_key

    @property
    def owner(self):
        assert self.__owner is not None
        return self.__owner

    @property
    def folder_id(self):
        assert self.__folder_pk is not None
        return self.__folder_pk


class PasswordKey(SymmetricKey):
    def __init__(self, password: str):
        self.__key = password

    def get_key(self):
        return self.__key


class UserKey(AsymmetricKey):
    def __init__(self, private_key: str, public_key: str):
        self.__private_key = private_key
        self.__public_key = public_key

    def get_decryption_key(self) -> str:
        return self.__private_key

    def get_encryption_key(self) -> str:
        return self.__public_key


class ContentKey(SymmetricKey):
    @staticmethod
    def create(key: str, encryption_version: str) -> "ContentKey":
        return ContentKey(
            key=OpenBox(data=key.encode("utf-8")), encryption_version=encryption_version
        )

    def __init__(
        self,
        key: Union[OpenBox, LockedBox] = None,
        encryption_version: Union[str, None] = None,
    ):
        assert encryption_version is not None

        self._encryption_version = encryption_version
        self.__key = key

        super().__init__()

    def encrypt(self, lock_key: "AsymmetricKey") -> "ContentKey":
        assert isinstance(self.__key, OpenBox)

        enc_key = lock_key.lock(self.__key)
        return ContentKey(key=enc_key)

    def decrypt(self, unlock_key: "AsymmetricKey") -> "ContentKey":
        assert isinstance(self.__key, LockedBox)

        key = unlock_key.unlock(self.__key)
        return ContentKey(key=key)

    def get_key(self) -> str:
        assert isinstance(self.__key, OpenBox)
        key = self.__key.decode("utf-8")
        return key
