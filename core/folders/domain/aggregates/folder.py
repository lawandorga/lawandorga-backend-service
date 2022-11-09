from typing import List, Optional, Union
from uuid import UUID, uuid4

from core.folders.domain.aggregates.upgrade import Upgrade
from core.folders.domain.external import IOwner
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    FolderKey,
    SymmetricKey,
)
from core.folders.domain.value_objects.keys.base import EncryptedAsymmetricKey
from core.seedwork.domain_layer import DomainError


class Folder(IOwner):
    @staticmethod
    def create(name: str = None, org_pk: int = None):
        pk = uuid4()
        return Folder(name=name, pk=pk, org_pk=org_pk)

    def __init__(
        self,
        name: str = None,
        pk: UUID = None,
        org_pk: int = None,
        keys: List[FolderKey] = None,
        parent_pk: UUID = None,
        upgrades: list[Upgrade] = None,
    ):
        assert name is not None and pk is not None
        assert all([k.is_encrypted for k in keys or []])

        self.__parent_pk = parent_pk
        self.__pk = pk
        self.__name = name
        self.__org_pk = org_pk
        self.__keys = keys if keys is not None else []
        self.__upgrades = upgrades if upgrades is not None else []

    def __str__(self):
        return "Folder {}".format(self.name)

    @property
    def org_pk(self):
        return self.__org_pk

    @property
    def keys(self):
        return self.__keys

    @property
    def pk(self):
        return self.__pk

    @property
    def parent(self):
        return self.__parent_pk

    @property
    def slug(self):
        return self.__pk

    @property
    def name(self):
        return self.__name

    @property
    def items(self):
        return []

    @property
    def upgrades(self):
        return self.__upgrades

    @property
    def encryption_version(self) -> Optional[str]:
        if len(self.__keys) == 0:
            return None

        versions = []
        for key in self.__keys:
            versions.append(key.key.origin)

        if not all([v == versions[0] for v in versions]):
            raise Exception("Not all folder keys have the same encryption version.")

        return versions[0]

    def has_access(self, owner: IOwner) -> bool:
        try:
            self.get_decryption_key(requestor=owner)
        except DomainError:
            return False
        return True

    def add_upgrade(self, upgrade: Upgrade):
        self.__upgrades.append(upgrade)

    def __reencrypt_all_keys(self, user: IOwner):
        enc_folder_key = self.__find_folder_key(user)
        folder_key = enc_folder_key.decrypt_self(user)
        old_key = folder_key.key

        # get a new folder key
        new_key = SymmetricKey.generate()

        # reencrypt upgrades
        for upgrade in self.__upgrades:
            upgrade.reencrypt(old_key, new_key)

        # reencrypt folder keys
        new_keys = []
        for key in self.__keys:
            new_folder_key = FolderKey(owner=key.owner, key=new_key)
            enc_new_key = new_folder_key.encrypt_self(
                key.owner.get_encryption_key(requestor=user)
            )
            new_keys.append(enc_new_key)

        # set
        self.__keys = new_keys

    def update_information(self, name=None):
        self.__name = name if name is not None else self.__name

    def check_encryption_version(self, user: IOwner):
        if self.encryption_version not in EncryptionWarehouse.get_highest_versions():
            self.__reencrypt_all_keys(user)

    def __find_folder_key(self, user: IOwner) -> FolderKey:
        parent_key: Optional[FolderKey] = None

        for key in self.__keys:
            if key.owner.slug == user.slug:
                return key
            if self.__parent_pk and key.owner.slug == self.__parent_pk:
                parent_key = key

        if parent_key is not None:
            return parent_key

        raise DomainError("No folder key was found for this user.")

    def get_encryption_key(self, *args, **kwargs) -> "SymmetricKey":
        assert len(self.__keys) > 0 and "requestor" in kwargs

        requestor = kwargs["requestor"]

        enc_folder_key = self.__find_folder_key(requestor)
        folder_key = enc_folder_key.decrypt_self(requestor)

        return folder_key.key

    def get_decryption_key(self, *args, **kwargs) -> "SymmetricKey":
        assert "requestor" in kwargs and len(self.__keys) > 0

        requestor = kwargs["requestor"]
        enc_folder_key = self.__find_folder_key(requestor)
        folder_key = enc_folder_key.decrypt_self(requestor)

        return folder_key.key

    def set_parent(self, folder: "Folder" = None, by: IOwner = None):
        assert folder is not None and by is not None

        self.__parent_pk = folder.pk

        parent_key = folder.get_encryption_key(requestor=by)

        if len(self.__keys) == 0:
            key = SymmetricKey.generate()

        else:
            enc_folder_key = self.__find_folder_key(by)
            folder_key = enc_folder_key.decrypt_self(by)
            key = folder_key.key

        access_key = FolderKey(
            owner=folder,
            key=key,
        )
        enc_access_key = access_key.encrypt_self(parent_key)

        self.__keys.append(enc_access_key)

    def move(self, target: "Folder"):
        pass

    def grant_access(self, to: IOwner, by: Optional[IOwner] = None):
        key: Union[AsymmetricKey, SymmetricKey]

        if len(self.__keys) == 0:
            key = SymmetricKey.generate()

        else:
            assert by is not None
            key = self.get_decryption_key(requestor=by)

        folder_key = FolderKey(
            owner=to,
            key=key,
        )

        lock_key = to.get_encryption_key()
        assert isinstance(lock_key, AsymmetricKey) or isinstance(
            lock_key, EncryptedAsymmetricKey
        )
        enc_key = folder_key.encrypt_self(lock_key)

        self.__keys.append(enc_key)

    def revoke_access(self, of: IOwner):
        new_keys = list(filter(lambda x: x.owner.slug != of.slug, self.__keys))

        if len(new_keys) == 0:
            raise DomainError(
                "You can not revoke access of this user as there would be no keys left."
            )

        self.__keys = new_keys
