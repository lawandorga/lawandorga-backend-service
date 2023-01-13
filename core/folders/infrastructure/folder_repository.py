import os.path
from datetime import timedelta
from typing import Any, Optional, Union
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.value_objects.folder_item import FolderItem
from core.folders.domain.value_objects.folder_key import FolderKey
from core.folders.domain.value_objects.parent_key import ParentKey
from core.folders.domain.value_objects.tree import FolderTree
from core.folders.models import FoldersFolder

PATH = os.path.abspath(__file__)


def get_cache_keys(key: Union[int, str]):
    value_key = "cache-key-{}".format(key)
    time_key = "cache-key-time-{}".format(key)
    return value_key, time_key


def get_cache_of_object(obj, key: Union[int, str]) -> Optional[Any]:
    value_key, time_key = get_cache_keys(key)

    if hasattr(obj, value_key) and hasattr(obj, time_key):
        if timezone.now() < getattr(obj, time_key):
            return getattr(obj, value_key)

        delattr(obj, time_key)
        delattr(obj, value_key)

    return None


def set_cache_on_object(obj, key: Union[int, str], value, seconds=4) -> None:
    value_key, time_key = get_cache_keys(key)

    time_value = timezone.now() + timedelta(seconds=seconds)
    setattr(obj, time_key, time_value)
    setattr(obj, value_key, value)


def delete_cache_of_object(obj, key: Union[int, str]) -> None:
    value_key, time_key = get_cache_keys(key)

    if hasattr(obj, value_key) and hasattr(obj, time_key):
        delattr(obj, time_key)
        delattr(obj, value_key)


class DjangoFolderRepository(FolderRepository):
    @classmethod
    def __db_folder_to_domain(
        cls,
        db_folder: FoldersFolder,
        folders: dict[UUID, FoldersFolder],
        users: dict[UUID, RlcUser],
    ) -> Folder:

        # find the parent
        parent: Optional[Folder] = None
        if db_folder.parent is not None:
            parent = cls.__db_folder_to_domain(
                folders[db_folder.parent], folders, users
            )

        # revive keys
        keys: list[Union[ParentKey, FolderKey]] = []
        for key in db_folder.keys:
            if key["type"] == "FOLDER":
                try:
                    owner = users[UUID(key["owner"])]
                except KeyError:
                    continue
                fk = FolderKey.create_from_dict(key, owner)
                keys.append(fk)

            elif key["type"] == "PARENT":
                pk = ParentKey.create_from_dict(key)
                keys.append(pk)

        # revive folder
        folder = Folder(
            name=db_folder.name,
            parent=parent,
            uuid=db_folder.uuid,
            org_pk=db_folder.org_id,
            keys=keys,
            stop_inherit=db_folder.stop_inherit,
        )

        # revive items
        for item in db_folder.items:
            name = item["name"] if "name" in item else "-"
            uuid = UUID(item["uuid"])
            repository = item["repository"]
            folder_item = FolderItem(name=name, repository=repository, uuid=uuid)
            folder.add_item(folder_item)

        # return
        return folder

    @classmethod
    def __db_folder_from_domain(cls, folder: Folder) -> FoldersFolder:
        keys = [k.as_dict() for k in folder.keys]
        items = [i.as_dict() for i in folder.items]

        parent_id: Optional[int] = None
        if folder.parent is not None:
            parent_id = cls.__db_folder_from_domain(folder.parent).pk

        if FoldersFolder.objects.filter(uuid=folder.uuid).exists():
            f = FoldersFolder.objects.get(uuid=folder.uuid)
            f._parent_id = parent_id
            f.name = folder.name
            f.org_id = folder.org_pk
            f.keys = keys
            f.items = items
            f.stop_inherit = folder.stop_inherit

        else:
            f = FoldersFolder(
                _parent_id=parent_id,
                uuid=folder.uuid,
                name=folder.name,
                org_id=folder.org_pk,
                keys=keys,
                items=items,
                stop_inherit=folder.stop_inherit,
            )

        return f

    @classmethod
    def __as_dict(cls, org_pk: int) -> dict[UUID, FoldersFolder]:
        folders = {}
        for f in list(FoldersFolder.query().filter(org_id=org_pk, deleted=False)):
            folders[f.uuid] = f
        return folders

    @classmethod
    def __users(cls, org_pk: int) -> dict[UUID, RlcUser]:
        users = {}
        for u in list(RlcUser.objects.filter(org_id=org_pk)):
            users[u.uuid] = u
        return users

    @classmethod
    def get_or_create_records_folder(cls, org_pk: int, user: IOwner) -> Folder:
        name = "Records"
        if FoldersFolder.objects.filter(
            org_id=org_pk, name=name, _parent=None
        ).exists():
            fs = FoldersFolder.objects.filter(org_id=org_pk, name=name, _parent=None)
            f1 = fs[0]
            if len(fs) > 1:
                for f2 in fs:
                    if len(f2.keys) > len(f1.keys):
                        f1 = f2
            return cls.get_dict(org_pk)[f1.uuid]
        folder = Folder.create(name=name, org_pk=org_pk)
        folder.grant_access(user)
        for u in RlcUser.objects.filter(org_id=org_pk).exclude(uuid=user.uuid):
            folder.grant_access(u, user)
        cls.save(folder)
        return cls.get_dict(org_pk)[folder.uuid]

    @classmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        assert isinstance(uuid, UUID)

        folders = cls.get_dict(org_pk)
        if uuid in folders:
            return folders[uuid]
        raise ObjectDoesNotExist()

    @classmethod
    def get_dict(cls, org_pk: int) -> dict[UUID, Folder]:
        cache_value = get_cache_of_object(cls, org_pk)
        if cache_value:
            return cache_value

        folders = cls.__as_dict(org_pk)
        users = cls.__users(org_pk)

        domain_folders = {}
        for i, f in folders.items():
            domain_folders[i] = cls.__db_folder_to_domain(f, folders, users)

        set_cache_on_object(cls, org_pk, domain_folders)

        return domain_folders

    @classmethod
    def get_list(cls, org_pk: int) -> list[Folder]:
        folders = cls.__as_dict(org_pk)
        users = cls.__users(org_pk)

        folders_list = []
        for folder in folders.values():
            folders_list.append(cls.__db_folder_to_domain(folder, folders, users))

        return folders_list

    @classmethod
    def save(cls, folder: Folder):
        db_folder = cls.__db_folder_from_domain(folder)
        db_folder.save()
        delete_cache_of_object(cls, folder.org_pk)

    @classmethod
    def delete(cls, folder: Folder):
        f = cls.__db_folder_from_domain(folder)
        f.deleted = True
        f.deleted_at = timezone.now()
        f.save()
        delete_cache_of_object(cls, folder.org_pk)

    @classmethod
    def tree(cls, user: IOwner, org_pk: int) -> FolderTree:
        return FolderTree(user, cls.get_list(org_pk))
