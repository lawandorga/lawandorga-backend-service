from typing import List, Optional, Union
from uuid import UUID, uuid4

from core.folders.domain.aggregates.upgrade import Upgrade
from core.folders.domain.external import IOwner
from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.encryption import EncryptionWarehouse
from core.folders.domain.value_objects.keys import (
    AsymmetricKey,
    FolderKey,
    SymmetricKey,
)
from core.folders.domain.value_objects.keys.base import EncryptedAsymmetricKey
from core.folders.domain.value_objects.keys.parent_key import ParentKey
from core.seedwork.domain_layer import DomainError


class Folder(IOwner):
    @staticmethod
    def create(name: Optional[str] = None, org_pk: Optional[int] = None):
        pk = uuid4()
        return Folder(name=name, pk=pk, org_pk=org_pk)

    def __init__(
        self,
        name: Optional[str] = None,
        pk: Optional[UUID] = None,
        org_pk: Optional[int] = None,
        keys: Optional[List[Union[FolderKey, ParentKey]]] = None,
        parent: Optional["Folder"] = None,
        upgrades: Optional[list[Upgrade]] = None,
    ):
        assert name is not None and pk is not None
        assert all([k.is_encrypted for k in keys or []])

        self.__parent = parent
        self.__pk = pk
        self.__name = name
        self.__org_pk = org_pk
        self.__keys = keys if keys is not None else []
        self.__upgrades = upgrades if upgrades is not None else []

    def __str__(self):
        return "Folder {}".format(self.name)

    def as_dict(self) -> StrDict:  # type: ignore
        return {"name": self.__name, "id": str(self.__pk)}

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
    def parent_pk(self):
        if self.__parent:
            return self.__parent.pk
        return None

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
    def content(self):
        content = []
        for upgrade in self.__upgrades:
            content += upgrade.content
        return content

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
        for key in self.__keys:
            if isinstance(key, FolderKey) and key.owner.slug == owner.slug:
                return True
        if self.__parent is None:
            return False
        return self.__parent.has_access(owner)

    def add_upgrade(self, upgrade: Upgrade):
        for upgrade in self.__upgrades:
            if upgrade.REPOSITORY == upgrade.REPOSITORY:
                raise ValueError(
                    "This folder already has an upgrade with the same repository."
                )
        self.__upgrades.append(upgrade)

    def __reencrypt_all_keys(self, user: IOwner):
        old_key = self.get_encryption_key(requestor=user)

        # get a new folder key
        new_key = SymmetricKey.generate()

        # reencrypt upgrades
        for upgrade in self.__upgrades:
            upgrade.reencrypt(old_key, new_key)

        # reencrypt keys
        new_keys: list[Union[FolderKey, ParentKey]] = []
        for key in self.__keys:
            if isinstance(key, ParentKey) and self.__parent is not None:
                new_parent_key = ParentKey(folder_pk=self.pk, key=new_key)
                enc_new_parent_key = new_parent_key.encrypt_self(
                    self.__parent.get_encryption_key(requestor=user)
                )
                new_keys.append(enc_new_parent_key)

            elif isinstance(key, FolderKey):
                new_folder_key = FolderKey(owner=key.owner, key=new_key)
                enc_new_folder_key = new_folder_key.encrypt_self(
                    key.owner.get_encryption_key(requestor=user)
                )
                new_keys.append(enc_new_folder_key)

            else:
                raise ValueError(
                    "This folder might have an parent key but its parent is None."
                )

        # set
        self.__keys = new_keys

    def update_information(self, name=None):
        self.__name = name if name is not None else self.__name

    def check_encryption_version(self, user: IOwner):
        if self.encryption_version not in EncryptionWarehouse.get_highest_versions():
            self.__reencrypt_all_keys(user)

    def __find_folder_key(self, user: IOwner) -> Optional[FolderKey]:
        for key in self.__keys:
            if isinstance(key, FolderKey) and key.owner.slug == user.slug:
                return key

        return None

    def __find_parent_key(self) -> Optional[ParentKey]:
        for key in self.__keys:
            if isinstance(key, ParentKey):
                return key

        return None

    def get_encryption_key(self, *args, **kwargs) -> "SymmetricKey":
        assert len(self.__keys) > 0 and "requestor" in kwargs

        requestor = kwargs["requestor"]

        enc_folder_key = self.__find_folder_key(requestor)
        if enc_folder_key:
            folder_key = enc_folder_key.decrypt_self(requestor)
            key = folder_key.key
            return key

        enc_parent_key = self.__find_parent_key()
        if self.__parent is not None and enc_parent_key:
            unlock_key = self.__parent.get_decryption_key(requestor=requestor)
            parent_key = enc_parent_key.decrypt_self(unlock_key)
            key = parent_key.key
            return key

        raise DomainError("No key was found for this folder.")

    def get_decryption_key(self, *args, **kwargs) -> "SymmetricKey":
        # the key is symmetric therefore the encryption and decryption key is the same
        return self.get_encryption_key(*args, **kwargs)

    def set_parent(
        self, folder: Optional["Folder"] = None, by: Optional[IOwner] = None
    ):
        assert folder is not None and by is not None

        self.__parent = folder

        # get the key of self
        if len(self.__keys) == 0:
            key = SymmetricKey.generate()

        else:
            key = self.get_decryption_key(requestor=by)

        parent_key = ParentKey(
            folder_pk=self.__pk,
            key=key,
        )

        # encrypt the new parent key
        lock_key = folder.get_encryption_key(requestor=by)
        enc_parent_key = parent_key.encrypt_self(lock_key)

        # add the parent key to keys
        self.__keys.append(enc_parent_key)

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
        prev_length = len(self.__keys)

        new_keys = list(
            filter(
                lambda x: isinstance(x, ParentKey) or x.owner.slug != of.slug,
                self.__keys,
            )
        )

        if prev_length == len(new_keys):
            raise DomainError("This user has no direct access to this folder.")

        if len(new_keys) == 0:
            raise DomainError(
                "You can not revoke access of this user as there would be no keys left."
            )

        self.__keys = new_keys
