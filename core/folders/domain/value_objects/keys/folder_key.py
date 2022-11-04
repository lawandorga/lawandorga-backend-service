from typing import Union

from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.keys import AsymmetricKey
from core.folders.domain.value_objects.keys.base import (
    EncryptedAsymmetricKey,
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.seedwork.domain_layer import DomainError


class FolderKey:
    def __init__(
        self,
        owner: IOwner = None,
        key: Union[
            AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey, EncryptedSymmetricKey
        ] = None,
    ):
        assert owner is not None and key is not None

        self.__owner = owner
        self.__key = key

        super().__init__()

    def __str__(self):
        return "FolderKey of {}".format(self.__owner.slug)

    def encrypt_with(
        self, key: Union[AsymmetricKey, EncryptedAsymmetricKey, SymmetricKey]
    ) -> "FolderKey":
        enc_key: Union[EncryptedAsymmetricKey, EncryptedSymmetricKey]

        if isinstance(self.__key, AsymmetricKey):
            enc_key = EncryptedAsymmetricKey.create(original=self.__key, key=key)

        elif isinstance(self.__key, SymmetricKey):
            enc_key = EncryptedSymmetricKey.create(original=self.__key, key=key)

        else:
            raise ValueError("The key has the wrong type.")

        return FolderKey(
            owner=self.__owner,
            key=enc_key,
        )

    def decrypt_with(self, owner: IOwner) -> "FolderKey":
        from core.folders.domain.aggregates.folder import Folder

        assert isinstance(self.__key, EncryptedAsymmetricKey) or isinstance(
            self.__key, EncryptedSymmetricKey
        )

        if owner.slug == self.__owner.slug:
            unlock_key = owner.get_key()

        elif isinstance(self.__owner, Folder):
            folder_key = self.__owner.find_folder_key(owner)
            unlock_key = folder_key.decrypt_with(owner).key

        else:
            raise DomainError("This folder key can not be decrypted.")

        key = self.key.decrypt(unlock_key)

        return FolderKey(
            owner=self.__owner,
            key=key,
        )

    @property
    def key(self):
        return self.__key

    @property
    def owner(self):
        return self.__owner

    @property
    def is_encrypted(self):
        return isinstance(self.__key, EncryptedAsymmetricKey)
