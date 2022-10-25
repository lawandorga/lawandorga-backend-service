from typing import Union

from core.folders.domain.external import IUser
from core.folders.domain.value_objects.box import LockedBox, OpenBox
from core.folders.domain.value_objects.keys.base import AsymmetricKey


class FolderKey(AsymmetricKey):
    @staticmethod
    def create(
        owner: IUser = None,
        # folder_pk: UUID = None,
        private_key: str = None,
        origin: str = None,
        public_key: str = None,
    ) -> "FolderKey":
        assert private_key is not None

        return FolderKey(
            owner=owner,
            # folder_pk=folder_pk,
            private_key=OpenBox(data=private_key.encode("utf-8")),
            origin=origin,
            public_key=public_key,
        )

    def __init__(
        self,
        owner: IUser = None,
        # folder_pk: UUID = None,
        private_key: Union[LockedBox, OpenBox] = None,
        public_key: str = None,
        origin: str = None,
    ):
        assert (
            owner is not None
            # and folder_pk is not None
            and private_key is not None
            and public_key is not None
            and origin is not None
        )

        # self.__folder_pk = folder_pk
        self.__owner = owner
        self.__public_key = public_key
        self._origin = origin
        self.__private_key = private_key

        super().__init__()

    def encrypt(self) -> "FolderKey":
        assert isinstance(self.__private_key, OpenBox)

        lock_key = self.__owner.get_key()
        enc_private_key = lock_key.lock(self.__private_key)
        return FolderKey(
            owner=self.__owner,
            # folder_pk=self.__folder_pk,
            private_key=enc_private_key,
            public_key=self.__public_key,
            origin=self.origin,
        )

    def decrypt(self) -> "FolderKey":
        assert isinstance(self.__private_key, LockedBox)

        unlock_key = self.__owner.get_key()
        private_key = unlock_key.unlock(self.__private_key)
        return FolderKey(
            owner=self.__owner,
            # folder_pk=self.__folder_pk,
            private_key=private_key,
            public_key=self.__public_key,
            origin=self.origin,
        )

    def get_encryption_key(self) -> str:
        return self.__public_key

    def get_decryption_key(self) -> str:
        assert isinstance(self.__private_key, OpenBox)
        return self.__private_key.decode("utf-8")

    @property
    def owner(self):
        return self.__owner

    @property
    def is_encrypted(self):
        return isinstance(self.__private_key, LockedBox)

    # @property
    # def folder_pk(self):
    #     return self.__folder_pk
