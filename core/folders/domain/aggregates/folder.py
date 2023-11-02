from typing import TYPE_CHECKING, Optional, Union
from uuid import UUID, uuid4

from core.folders.domain.aggregates.item import Item
from core.folders.domain.value_objects.asymmetric_key import (
    AsymmetricKey,
    EncryptedAsymmetricKey,
)
from core.folders.domain.value_objects.folder_item import FolderItem
from core.folders.domain.value_objects.folder_key import (
    EncryptedFolderKeyOfUser,
    FolderKeyOfUser,
)
from core.folders.domain.value_objects.parent_key import ParentKey
from core.folders.domain.value_objects.symmetric_key import SymmetricKey
from core.seedwork.domain_layer import DomainError

from seedwork.types import JsonDict

if TYPE_CHECKING:
    from core.auth.models.org_user import RlcUser
    from core.rlc.models.group import Group


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
        keys: Optional[list[EncryptedFolderKeyOfUser]] = None,
        enc_parent_key: Optional[ParentKey] = None,
        parent: Optional["Folder"] = None,
        items: Optional[list[FolderItem]] = None,
        stop_inherit: bool = False,
        restricted: bool = False,
    ):
        assert name is not None and uuid is not None
        assert all([k.is_encrypted for k in keys or []])

        self.__parent = parent
        self.__uuid = uuid
        self.__name = name
        self.__org_pk = org_pk
        self.__enc_parent_key = enc_parent_key
        self.__stop_inherit = stop_inherit
        self.__keys = keys if keys is not None else []
        self.__items = items if items is not None else []
        self.__restricted = restricted

    def __str__(self):
        return "Folder {}".format(self.name)

    def as_dict(self) -> JsonDict:
        return {
            "name": self.__name,
            "uuid": str(self.__uuid),
            "stop_inherit": self.stop_inherit,
        }

    def __eq__(self, other):
        if not isinstance(other, Folder):
            return False
        return self.uuid == other.uuid

    @property
    def restricted(self):
        return self.__restricted

    @property
    def org_pk(self):
        return self.__org_pk

    @property
    def stop_inherit(self):
        return self.__stop_inherit

    @property
    def enc_parent_key(self):
        return self.__enc_parent_key

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
    def items(self) -> list[FolderItem]:
        return self.__items

    @property
    def encryption_version(self) -> Optional[str]:
        if len(self.__keys) == 0 and self.enc_parent_key is None:
            return None

        versions = []
        for key in self.__keys:
            versions.append(key.key_origin)

        if not all([v == versions[0] for v in versions]):
            raise Exception("Not all folder keys have the same encryption version.")

        return versions[0]

    def invalidate_keys_of(self, owner: "RlcUser"):
        new_keys: list[EncryptedFolderKeyOfUser] = []
        for key in self.__keys:
            new_key = key
            if (
                isinstance(key, EncryptedFolderKeyOfUser)
                and key.owner_uuid == owner.uuid
            ):
                new_key = key.invalidate_self()
            new_keys.append(new_key)
        self.__keys = new_keys

    def has_invalid_keys(self, owner: "RlcUser") -> bool:
        for key in self.__keys:
            if (
                isinstance(key, EncryptedFolderKeyOfUser)
                and key.owner_uuid == owner.uuid
                and not key.is_valid
            ):
                return True
        return False

    def fix_keys(self, of: "RlcUser", by: "RlcUser"):
        new_keys: list[EncryptedFolderKeyOfUser] = []
        fixed = False

        for key in self.__keys:
            enc_new_key = key
            if (
                isinstance(key, EncryptedFolderKeyOfUser)
                and key.owner_uuid == of.uuid
                and not key.is_valid
            ):
                s_key = self.get_decryption_key(requestor=by)
                new_key = FolderKeyOfUser(owner_uuid=of.uuid, key=s_key)
                enc_key = of.get_encryption_key()
                enc_new_key = new_key.encrypt_self(enc_key)
                fixed = True
            new_keys.append(enc_new_key)

        if not fixed:
            raise ValueError("The user has no invalid keys for this folder.")

        self.__keys = new_keys

    def has_access(self, owner: Union["RlcUser", "Group"]) -> bool:
        for key in self.__keys:
            if (
                isinstance(key, EncryptedFolderKeyOfUser)
                and key.owner_uuid == owner.uuid
                and key.is_valid
            ):
                return True
        if self.__parent is None or self.__stop_inherit:
            return False
        return self.__parent.has_access(owner)

    def restrict(self) -> None:
        self.__restricted = True

    def _has_keys(self, owner: Union["RlcUser", "Group"]) -> bool:
        for key in self.__keys:
            if (
                isinstance(key, EncryptedFolderKeyOfUser)
                and key.owner_uuid == owner.uuid
            ):
                return True
        if self.__parent is None or self.__stop_inherit:
            return False
        return self.__parent._has_keys(owner)

    def __contains(self, item: Union[Item, FolderItem]):
        contains = False
        for i in self.items:
            if i.uuid == item.uuid:
                contains = True
                break
        return contains

    def __add_item(self, item: Union[Item, FolderItem]):
        if isinstance(item, FolderItem):
            folder_item = item
        else:
            folder_item = FolderItem.create_from_item(item)

        self.__items.append(folder_item)

    def add_item(self, item: Union[Item, FolderItem]):
        if self.__contains(item):
            raise ValueError("This folder already contains this item.")

        self.__add_item(item)

    def update_item(self, item: Union[Item, FolderItem]):
        if not self.__contains(item):
            raise ValueError("This folder does not contain this item.")

        self.remove_item(item.uuid)
        self.__add_item(item)

    def remove_item(self, uuid: UUID):
        new_items_1 = filter(lambda x: x.uuid != uuid, self.__items)
        new_items_2 = list(new_items_1)
        self.__items = new_items_2

    def update_information(self, name=None, force=False):
        if not force and name is not None and self.__restricted:
            raise DomainError(
                "The name of this folder can not be changed as it contains a record."
            )
        self.__name = name if name is not None else self.__name

    def __find_folder_key(self, user: "RlcUser") -> Optional[EncryptedFolderKeyOfUser]:
        for key in self.__keys:
            if (
                isinstance(key, EncryptedFolderKeyOfUser)
                and key.owner_uuid == user.uuid
                and key.is_valid
            ):
                return key

        return None

    def __find_parent_key(self) -> Optional[ParentKey]:
        for key in self.__keys:
            if isinstance(key, ParentKey):
                return key

        return None

    def __get_encryption_key_from_user_keys(
        self, requestor: "RlcUser"
    ) -> Optional["SymmetricKey"]:
        enc_folder_key = self.__find_folder_key(requestor)
        if enc_folder_key:
            folder_key = enc_folder_key.decrypt_self(requestor)
            key = folder_key.key
            assert isinstance(key, SymmetricKey)
            return key
        return None

    def __get_encryption_key_from_parent(
        self, requestor: "RlcUser"
    ) -> Optional["SymmetricKey"]:
        if self.__stop_inherit:
            return None

        enc_parent_key = self.__enc_parent_key
        if self.__parent is not None and enc_parent_key:
            unlock_key = self.__parent.get_encryption_key(requestor=requestor)
            parent_key = enc_parent_key.decrypt_self(unlock_key)
            key = parent_key.key
            assert isinstance(key, SymmetricKey)
            return key

        return None

    def get_encryption_key(self, requestor: "RlcUser") -> "SymmetricKey":
        assert len(self.__keys) or self.enc_parent_key is not None

        key = self.__get_encryption_key_from_user_keys(requestor)
        if key:
            return key

        key = self.__get_encryption_key_from_parent(requestor)
        if key:
            return key

        raise DomainError("No key was found for this folder.")

    def get_decryption_key(self, requestor: "RlcUser") -> "SymmetricKey":
        # the key is symmetric therefore the encryption and decryption key is the same
        return self.get_encryption_key(requestor=requestor)

    def __set_parent(self, parent: "Folder", by: "RlcUser"):
        self.__parent = parent

        # get the key of self
        if len(self.__keys) == 0 and self.__enc_parent_key is None:
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
        self.__enc_parent_key = enc_parent_key

    def set_parent(self, parent: "Folder", by: "RlcUser"):
        assert by is not None

        if self.__parent is not None:
            raise DomainError("This folder already has a parent folder.")

        if parent.restricted:
            raise DomainError(
                "The parent folder is restricted, probably contains a "
                "record and therefore you can not add subfolders."
            )

        self.__set_parent(parent, by)

    def allow_inheritance(self):
        self.__stop_inherit = False

    def stop_inheritance(self):
        self.__stop_inherit = True

    def move(self, target: "Folder", by: "RlcUser"):
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

        self.__enc_parent_key = None

        self.__parent = None
        self.set_parent(target, by)

    def grant_access(
        self, to: Union["RlcUser", "Group"], by: Optional["RlcUser"] = None
    ):
        key: Union[AsymmetricKey, SymmetricKey]

        if self._has_keys(to):
            raise DomainError("This entity already has keys for this folder.")

        if len(self.__keys) == 0 and self.__enc_parent_key is None:
            key = SymmetricKey.generate()

        else:
            assert by is not None
            key = self.get_decryption_key(requestor=by)

        folder_key = FolderKeyOfUser(
            owner_uuid=to.uuid,
            key=key,
        )

        lock_key: Union[AsymmetricKey, SymmetricKey, EncryptedAsymmetricKey]

        lock_key = to.get_encryption_key(user=by)  # type: ignore

        enc_key = folder_key.encrypt_self(lock_key)

        self.__keys.append(enc_key)

    def revoke_access(self, of: Union["RlcUser", "Group"]):
        prev_length = len(self.__keys)

        new_keys: list[EncryptedFolderKeyOfUser] = list(
            filter(
                lambda x: x.owner_uuid != of.uuid,
                self.__keys,
            )
        )

        if prev_length == len(new_keys):
            raise DomainError("This user has no direct access to this folder.")

        if (self.__stop_inherit and len(new_keys) <= 1) or len(new_keys) == 0:
            raise DomainError(
                "You can not revoke access of this user as there would not be enough keys left."
            )

        self.__keys = new_keys
