from typing import List, Optional, Union
from uuid import UUID, uuid4

from core.folders.domain.aggregates.item import Item
from core.folders.domain.external import IOwner
from core.folders.domain.types import StrDict
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.folder_item import FolderItem
from core.folders.domain.value_objects.folder_key import FolderKey
from core.folders.domain.value_objects.parent_key import ParentKey
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.seedwork.domain_layer import DomainError


class Folder:
    @staticmethod
    def create(
        name: Optional[str] = None,
        org_pk: Optional[int] = None,
        stop_inherit: bool = False,
    ):
        pk = uuid4()
        return Folder(name=name, uuid=pk, org_pk=org_pk, stop_inherit=stop_inherit)

    def __init__(
        self,
        name: Optional[str] = None,
        uuid: Optional[UUID] = None,
        org_pk: Optional[int] = None,
        keys: Optional[List[Union[FolderKey, ParentKey]]] = None,
        parent: Optional["Folder"] = None,
        items: Optional[list[FolderItem]] = None,
        stop_inherit: bool = False,
    ):
        assert name is not None and uuid is not None
        assert all([k.is_encrypted for k in keys or []])

        self.__parent = parent
        self.__uuid = uuid
        self.__name = name
        self.__org_pk = org_pk
        self.__stop_inherit = stop_inherit
        self.__keys = keys if keys is not None else []
        self.__items = items if items is not None else []

    def __str__(self):
        return "Folder {}".format(self.name)

    def as_dict(self) -> StrDict:
        return {
            "name": self.__name,
            "id": str(self.__uuid),
            "stop_inherit": self.stop_inherit,
        }

    @property
    def org_pk(self):
        return self.__org_pk

    @property
    def stop_inherit(self):
        return self.__stop_inherit

    @property
    def keys(self):
        return self.__keys

    @property
    def parent(self):
        return self.__parent

    @property
    def uuid(self):
        return self.__uuid

    @property
    def parent_uuid(self):
        if self.__parent:
            return self.__parent.uuid
        return None

    @property
    def name(self):
        return self.__name

    @property
    def items(self):
        return self.__items

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

    def invalidate_keys_of(self, owner: IOwner):
        new_keys: list[Union[FolderKey, ParentKey]] = []
        for key in self.__keys:
            new_key = key
            if isinstance(key, FolderKey) and key.owner.uuid == owner.uuid:
                new_key = key.invalidate_self()
            new_keys.append(new_key)
        self.__keys = new_keys

    def has_invalid_keys(self, owner: IOwner) -> bool:
        for key in self.__keys:
            if (
                isinstance(key, FolderKey)
                and key.owner.uuid == owner.uuid
                and not key.is_valid
            ):
                return True
        return False

    def fix_keys(self, of: IOwner, by: IOwner):
        new_keys = []
        fixed = False

        for key in self.__keys:
            enc_new_key = key
            if (
                isinstance(key, FolderKey)
                and key.owner.uuid == of.uuid
                and not key.is_valid
            ):
                s_key = self.get_decryption_key(requestor=by)
                new_key = FolderKey(owner=of, key=s_key)
                enc_key = of.get_encryption_key()
                enc_new_key = new_key.encrypt_self(enc_key)
                fixed = True
            new_keys.append(enc_new_key)

        if not fixed:
            raise ValueError("The user has no invalid keys for this folder.")

        self.__keys = new_keys

    def has_access(self, owner: IOwner) -> bool:
        for key in self.__keys:
            if (
                isinstance(key, FolderKey)
                and key.owner.uuid == owner.uuid
                and key.is_valid
            ):
                return True
        if self.__parent is None or self.__stop_inherit:
            return False
        return self.__parent.has_access(owner)

    def _has_keys(self, owner: IOwner) -> bool:
        for key in self.__keys:
            if isinstance(key, FolderKey) and key.owner.uuid == owner.uuid:
                return True
        if self.__parent is None or self.__stop_inherit:
            return False
        return self.__parent._has_keys(owner)

    def __add_item(self, item: Union[Item, FolderItem]):
        if isinstance(item, FolderItem):
            folder_item = item
        else:
            item.set_folder(self)
            folder_item = FolderItem.create_from_item(item)

        self.__items.append(folder_item)

    def add_item(self, item: Union[Item, FolderItem]):
        for i in self.__items:
            if i.uuid == item.uuid:
                raise ValueError("This folder already contains this item.")

        self.__add_item(item)

    def update_item(self, item: Union[Item, FolderItem]):
        self.remove_item(item)
        self.__add_item(item)

    def remove_item(self, item: Union[Item, FolderItem]):
        new_items_1 = filter(lambda x: x.uuid != item.uuid, self.__items)
        new_items_2 = list(new_items_1)
        self.__items = new_items_2

    def __todo_reencrypt_all_keys(self, user: IOwner):
        # this method is not ready yet, because the keys of the children need to be reencrypted as well

        # old_key = self.get_encryption_key(requestor=user)

        # get a new folder key
        new_key = SymmetricKey.generate()

        # reencrypt keys
        new_keys: list[Union[FolderKey, ParentKey]] = []
        for key in self.__keys:
            if isinstance(key, ParentKey) and self.__parent is not None:
                new_parent_key = ParentKey(folder_uuid=self.uuid, key=new_key)
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
        # if self.encryption_version not in EncryptionWarehouse.get_highest_versions():
        #     self.__reencrypt_all_keys(user)
        pass

    def __find_folder_key(self, user: IOwner) -> Optional[FolderKey]:
        for key in self.__keys:
            if (
                isinstance(key, FolderKey)
                and key.owner.uuid == user.uuid
                and key.is_valid
            ):
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

        if not self.__stop_inherit:
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

    def __set_parent(self, parent: "Folder", by: Optional[IOwner] = None):
        self.__parent = parent

        # get the key of self
        if len(self.__keys) == 0:
            key = SymmetricKey.generate()

        else:
            key = self.get_decryption_key(requestor=by)

        parent_key = ParentKey(
            folder_uuid=self.__uuid,
            key=key,
        )

        # encrypt the new parent key
        lock_key = parent.get_encryption_key(requestor=by)
        enc_parent_key = parent_key.encrypt_self(lock_key)

        # add the parent key to keys
        self.__keys.append(enc_parent_key)

    def set_parent(self, parent: "Folder", by: Optional[IOwner] = None):
        assert by is not None

        if self.__parent is not None:
            raise DomainError("This folder already has a parent folder.")

        self.__set_parent(parent, by)

    def allow_inheritance(self):
        self.__stop_inherit = False

    def stop_inheritance(self):
        self.__stop_inherit = True

    def move(self, target: "Folder", by: IOwner):
        if not self.has_access(by):
            raise DomainError("You have no access to this folder.")

        if not target.has_access(by):
            raise DomainError("You have no access to the target folder.")

        parent = target.parent
        while parent is not None:
            if parent.uuid == self.uuid:
                raise DomainError(
                    "A folder can not be moved to one of its descendants."
                )
            parent = parent.parent

        self.__keys = [k for k in self.__keys if isinstance(k, FolderKey)]
        self.__parent = None
        self.set_parent(target, by)

    def grant_access(self, to: IOwner, by: Optional[IOwner] = None):
        key: Union[AsymmetricKey, SymmetricKey]

        if self._has_keys(to):
            raise DomainError("This user already has keys for this folder.")

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
                lambda x: isinstance(x, ParentKey) or x.owner.uuid != of.uuid,
                self.__keys,
            )
        )

        if prev_length == len(new_keys):
            raise DomainError("This user has no direct access to this folder.")

        if (self.__stop_inherit and len(new_keys) <= 1) or len(new_keys) == 0:
            raise DomainError(
                "You can not revoke access of this user as there would be not enough keys left."
            )

        self.__keys = new_keys
