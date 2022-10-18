import abc
from typing import Literal, Optional
from uuid import UUID


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
    def __init__(self, key: str):
        self.__key = key

    def get_key(self) -> str:
        return self.__key
