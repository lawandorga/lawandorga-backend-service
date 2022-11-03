from typing import Optional, Union

from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.seedwork.domain_layer import DomainError


class FolderKey:
    @staticmethod
    def create(
        owner: IOwner = None,
        private_key: str = None,
        origin: str = None,
        public_key: str = None,
    ) -> "FolderKey":
        assert private_key is not None

        return FolderKey(
            owner=owner,
            private_key=OpenBox(data=private_key.encode("utf-8")),
            origin=origin,
            public_key=public_key,
        )

    def __init__(
        self,
        owner: IOwner = None,
        private_key: Union[LockedBox, OpenBox] = None,
        public_key: str = None,
        origin: str = None,
    ):
        assert (
            owner is not None
            and private_key is not None
            and public_key is not None
            and origin is not None
        )

        self.__owner = owner
        self.__public_key = public_key
        self._origin = origin
        self.__private_key = private_key

        super().__init__()

    def __str__(self):
        return "FolderKey of {}".format(self.__owner.slug)

    def encrypt(self) -> "FolderKey":
        assert isinstance(self.__private_key, OpenBox)

        lock_key = self.__owner.get_key()
        enc_private_key = lock_key.lock(self.__private_key)
        return FolderKey(
            owner=self.__owner,
            private_key=enc_private_key,
            public_key=self.__public_key,
            origin=self.origin,
        )

    def decrypt(self, owner: IOwner) -> "FolderKey":
        from core.folders.domain.aggregates.folder import Folder

        assert isinstance(self.__private_key, LockedBox)

        if owner.slug == self.__owner.slug:
            unlock_key = self.__owner.get_key()

        elif isinstance(self.__owner, Folder):
            folder_key = self.__owner.find_folder_key(owner)
            unlock_key = folder_key.decrypt(owner)

        else:
            raise DomainError("This folder key can not be decrypted.")

        private_key = unlock_key.unlock(self.__private_key)

        return FolderKey(
            owner=self.__owner,
            private_key=private_key,
            public_key=self.__public_key,
            origin=self.origin,
        )

    def get_encryption_key(self) -> str:
        return self.__public_key

    def get_decryption_key(self) -> Optional[str]:
        if not isinstance(self.__private_key, OpenBox):
            return None
        return self.__private_key.decode("utf-8")

    @property
    def owner(self):
        return self.__owner

    @property
    def is_encrypted(self):
        return isinstance(self.__private_key, LockedBox)
