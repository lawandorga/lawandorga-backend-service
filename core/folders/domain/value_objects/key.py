import abc
from typing import Literal, Optional, Type, Union
from uuid import UUID

from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.encryption import (
    AsymmetricEncryption,
    SymmetricEncryption,
)


class Key(abc.ABC):
    KEY_TYPE: Literal["SYMMETRIC", "ASYMMETRIC", None] = None


class AsymmetricKey(Key):
    KEY_TYPE: Literal["ASYMMETRIC"] = "ASYMMETRIC"

    @abc.abstractmethod
    def get_decryption_key(self) -> str:
        pass

    @abc.abstractmethod
    def get_encryption_key(self) -> str:
        pass


class SymmetricKey(Key):
    KEY_TYPE: Literal["SYMMETRIC"] = "SYMMETRIC"

    @abc.abstractmethod
    def get_key(self) -> str:
        pass


class FolderKey(AsymmetricKey):
    def __init__(
        self,
        user: Optional[UUID] = None,
        # folder: "Folder",
        private_key: Optional[str] = None,
        public_key: Optional[str] = None
        # correct: bool,
        # missing: bool,
    ):
        self.__user = user
        # self.__folder = folder
        self.__private_key = private_key
        self.__public_key = public_key
        # self.__encryption = encryption
        # self.__correct = correct
        # self.__missing = missing

    def get_encryption_key(self) -> str:
        assert self.__public_key is not None
        return self.__public_key

    def get_decryption_key(self) -> str:
        assert self.__private_key is not None
        return self.__private_key

    @property
    def user(self):
        assert self.__user is not None
        return self.__user


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
    __key: Union[OpenBox, LockedBox]

    def __init__(
        self,
        key: Optional[str] = None,
        enc_key: Optional[bytes] = None,
        encryption_class: Optional[
            Union[Type[AsymmetricEncryption], Type[SymmetricEncryption]]
        ] = None,
    ):
        if key:
            assert key is not None
            bytes_key = key.encode("utf-8")
            self.__key = OpenBox(data=bytes_key)

        elif enc_key:
            assert enc_key is not None and encryption_class is not None
            self.__key = LockedBox(enc_data=enc_key, encryption_class=encryption_class)

    def encrypt(
        self, lock_key: "AsymmetricKey", encryption_class: Type[AsymmetricEncryption]
    ) -> "ContentKey":
        assert isinstance(self.__key, OpenBox)

        enc_key = self.__key.lock(lock_key, encryption_class)
        return ContentKey(enc_key=enc_key, encryption_class=encryption_class)

    def decrypt(self, unlock_key: "AsymmetricKey") -> "ContentKey":
        assert isinstance(self.__key, LockedBox)

        bytes_key = self.__key.unlock(unlock_key)
        key = bytes_key.decode("utf-8")
        return ContentKey(key=key)

    def get_key(self) -> str:
        assert isinstance(self.__key, OpenBox)
        key = self.__key.decode("utf-8")
        return key
