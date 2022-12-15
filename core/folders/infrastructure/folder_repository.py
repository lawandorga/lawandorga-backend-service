import os.path
from typing import Optional, Type, Union, cast
from uuid import UUID

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.external import IOwner
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.item import ItemRepository
from core.folders.domain.value_objects.folder_key import FolderKey
from core.folders.domain.value_objects.parent_key import ParentKey
from core.folders.domain.value_objects.tree import FolderTree
from core.folders.models import FoldersFolder
from core.seedwork.repository import RepositoryWarehouse

PATH = os.path.abspath(__file__)


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
                owner = users[UUID(key["owner"])]
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
            item_repository = cast(
                Type[ItemRepository], RepositoryWarehouse.get(item["repository"])
            )
            try:
                i = item_repository.retrieve(uuid=item["uuid"])
            except ObjectDoesNotExist:
                continue
            folder.add_item(i)

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
    def __get_cache_key(cls, org_pk: int):
        return "{}---{}".format(PATH, org_pk)

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
            f = FoldersFolder.objects.get(org_id=org_pk, name=name, _parent=None)
            return cls.get_dict(org_pk)[f.uuid]
        folder = Folder.create(name=name, org_pk=org_pk)
        folder.grant_access(user)
        for u in RlcUser.objects.filter(org_id=org_pk).exclude(uuid=user.uuid):
            folder.grant_access(u, user)
        cls.save(folder)
        return cls.get_dict(org_pk)[folder.uuid]

    @classmethod
    def retrieve(cls, org_pk: int, uuid: UUID) -> Folder:
        folders = cls.get_dict(org_pk)
        if uuid in folders:
            return folders[uuid]
        raise ObjectDoesNotExist()

    @classmethod
    def get_dict(cls, org_pk: int) -> dict[UUID, Folder]:
        cache_value = cache.get(cls.__get_cache_key(org_pk), None)
        if cache_value:
            return cache_value

        folders = cls.__as_dict(org_pk)
        users = cls.__users(org_pk)

        domain_folders = {}
        for i, f in folders.items():
            domain_folders[i] = cls.__db_folder_to_domain(f, folders, users)

        cache.set(cls.__get_cache_key(org_pk), domain_folders)

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
        cache.delete(cls.__get_cache_key(folder.org_pk))

    @classmethod
    def delete(cls, folder: Folder):
        f = cls.__db_folder_from_domain(folder)
        f.deleted = True
        f.deleted_at = timezone.now()
        f.save()
        cache.delete(cls.__get_cache_key(folder.org_pk))

    @classmethod
    def tree(cls, org_pk: int) -> FolderTree:
        return FolderTree(cls.get_list(org_pk))
