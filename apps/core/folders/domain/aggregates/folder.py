from typing import List, Optional
from uuid import UUID

from apps.core.folders.domain.value_objects.asymmetric_encryption import (
    AsymmetricEncryption,
)
from apps.static.domain_layer import DomainError

from .content import Content


class Key:
    def __init__(
        self,
        pk: str,
        user: str,
        encryption: AsymmetricEncryption,
        correct: bool,
        missing: bool,
    ):
        self.__pk = pk
        self.__user = user
        self.__encryption = encryption
        self.__correct = correct
        self.__missing = missing

    def get_private_key(self, private_key_user: str) -> str:
        try:
            # TODO: decrypt enc_private_key
            private_key = ""
        except Exception:
            self.__correct = False
            raise ValueError("The key could not be decrypted.")

        return private_key

    @property
    def user(self):
        return self.__user

    @property
    def correct(self):
        return self.__correct

    @property
    def missing(self):
        return self.__missing


class Folder:
    def __init__(
        self,
        pk: UUID,
        name: str,
        parent: Optional["Folder"],
        public_key: str,
        children: List[Content],
        keys: List[Key],
    ):
        self.__pk = pk
        self.__name = name
        self.__parent = parent
        self.__public_key = public_key
        self.__children = children
        self.__keys = keys

    @property
    def public_key(self):
        return self.__public_key

    def get_private_key(self, user: str, private_key_user: str):
        possible_keys = list(
            filter(
                lambda k: k.user == user and not k.missing and k.correct, self.__keys
            )
        )

        if len(possible_keys) > 1:
            raise DomainError("More than one possible key detected.")

        if len(possible_keys) == 0:
            raise DomainError("No keys detected to access content in this folder.")

        key = possible_keys[0]

        try:
            private_key = key.get_private_key(private_key_user)
        except ValueError:
            raise DomainError(
                "The key to access content of this folder is not working."
            )

        return private_key
