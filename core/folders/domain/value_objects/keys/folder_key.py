from typing import Union

from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.keys import AsymmetricKey
from core.folders.domain.value_objects.keys.base import EncryptedAsymmetricKey
from core.seedwork.domain_layer import DomainError


class FolderKey:
    def __init__(
        self,
        owner: IOwner = None,
        key: Union[AsymmetricKey, EncryptedAsymmetricKey] = None,
    ):
        assert owner is not None and key is not None

        self.__owner = owner
        self.__key = key

        super().__init__()

    def __str__(self):
        return "FolderKey of {}".format(self.__owner.slug)

    def encrypt(self) -> "FolderKey":
        assert isinstance(self.__key, AsymmetricKey)

        enc_key = EncryptedAsymmetricKey.create(self.__key, self.__owner.get_key())
        return FolderKey(
            owner=self.__owner,
            key=enc_key,
        )

    def decrypt(self, owner: IOwner) -> "FolderKey":
        from core.folders.domain.aggregates.folder import Folder

        assert isinstance(self.__key, EncryptedAsymmetricKey)

        if owner.slug == self.__owner.slug:
            unlock_key = owner.get_key()

        elif isinstance(self.__owner, Folder):
            folder_key = self.__owner.find_folder_key(owner)
            unlock_key = folder_key.decrypt(owner).key

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
