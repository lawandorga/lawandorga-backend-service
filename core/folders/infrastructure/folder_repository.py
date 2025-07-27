from typing import Any, Optional
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.domain.repositories.item import ItemRepository
from core.folders.domain.value_objects.folder_item import FolderItem
from core.folders.domain.value_objects.folder_key import (
    EncryptedFolderKeyOfGroup,
    EncryptedFolderKeyOfUser,
)
from core.folders.domain.value_objects.parent_key import ParentKey
from core.folders.models import FOL_ClosureTable, FOL_Folder

from seedwork.functional import list_map


class DjangoFolderRepository(FolderRepository):
    def __db_folder_to_domain(
        self,
        db_folder: FOL_Folder,
        folders: dict[int, FOL_Folder],
    ) -> Folder:
        # find the parent
        parent: Optional[Folder] = None
        if db_folder._parent_id is not None:
            try:
                parent_db = folders[db_folder._parent_id]
            except KeyError:
                raise ObjectDoesNotExist("parent folder not found")
            parent = self.__db_folder_to_domain(parent_db, folders)

        # revive keys
        enc_parent_key: Optional[ParentKey] = None
        if db_folder.enc_parent_key is not None:
            enc_parent_key = ParentKey.create_from_dict(db_folder.enc_parent_key)

        user_keys: list[EncryptedFolderKeyOfUser] = []
        for key in db_folder.keys:
            if key["type"] == "PARENT":
                p_key = ParentKey.create_from_dict(key)
                enc_parent_key = p_key
                continue

            f_key = EncryptedFolderKeyOfUser.create_from_dict(key)
            user_keys.append(f_key)

        group_keys: list[EncryptedFolderKeyOfGroup] = []
        for key in db_folder.group_keys if db_folder.group_keys else []:
            g_key = EncryptedFolderKeyOfGroup.create_from_dict(key)
            group_keys.append(g_key)

        # revive folder
        folder = Folder(
            name=db_folder.name,
            parent=parent,
            uuid=db_folder.uuid,
            org_pk=db_folder.org_id,
            keys=user_keys,
            enc_parent_key=enc_parent_key,
            group_keys=group_keys,
            stop_inherit=db_folder.stop_inherit,
            restricted=db_folder.restricted,
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

    def __db_folder_from_domain(self, folder: Folder) -> FOL_Folder:
        keys = [k.as_dict() for k in folder.keys]
        items = [i.as_dict() for i in folder.items]
        group_keys = [k.as_dict() for k in folder.group_keys]

        parent_id: Optional[int] = None
        if folder.parent is not None:
            parent_id = self.__db_folder_from_domain(folder.parent).pk

        enc_parent_key: Optional[dict[str, Any]] = None
        if folder.enc_parent_key is not None:
            enc_parent_key = folder.enc_parent_key.as_dict()

        if FOL_Folder.objects.filter(uuid=folder.uuid).exists():
            f = FOL_Folder.objects.get(uuid=folder.uuid)
            f._parent_id = parent_id
            f.name = folder.name
            assert folder.org_pk is not None
            f.org_id = folder.org_pk
            f.keys = keys
            f.group_keys = group_keys  # type: ignore
            f.items = items
            f.stop_inherit = folder.stop_inherit
            f.restricted = folder.restricted
            f.enc_parent_key = enc_parent_key  # type: ignore

        else:
            f = FOL_Folder(
                _parent_id=parent_id,
                uuid=folder.uuid,
                name=folder.name,
                org_id=folder.org_pk,
                keys=keys,
                group_keys=group_keys,
                items=items,
                stop_inherit=folder.stop_inherit,
                restricted=folder.restricted,
                enc_parent_key=enc_parent_key,
            )

        return f

    def __as_id_dict(self, org_pk: int) -> dict[int, FOL_Folder]:
        folders = {}
        for f in list(FOL_Folder.objects.filter(org_id=org_pk, deleted=False)):
            folders[f.pk] = f
        return folders

    def get_or_create_records_folder(self, org_pk: int, user: "OrgUser") -> Folder:
        name = "Records"
        if FOL_Folder.objects.filter(
            org_id=org_pk, name=name, _parent=None, deleted=False
        ).exists():
            fs = FOL_Folder.objects.filter(
                org_id=org_pk, name=name, _parent=None, deleted=False
            )
            f1 = fs[0]
            if len(fs) > 1:
                for f2 in fs:
                    if len(f2.keys) > len(f1.keys):
                        f1 = f2
            return self.get_dict(org_pk)[f1.uuid]
        folder = Folder.create(name=name, org_pk=org_pk)
        folder.grant_access(user)
        for u in OrgUser.objects.filter(org_id=org_pk).exclude(uuid=user.uuid):
            folder.grant_access(u, user)
        self.save(folder)
        return self.get_dict(org_pk)[folder.uuid]

    def retrieve(self, org_pk: int, uuid: UUID) -> Folder:
        assert isinstance(uuid, UUID)

        db_folder = FOL_Folder.objects.filter(uuid=uuid, org_id=org_pk).get()
        closures = FOL_ClosureTable.objects.filter(
            child_id=db_folder.pk
        ).select_related("parent")
        db_parents = list_map(closures, lambda c: c.parent)
        db_parents_dict = {f.pk: f for f in db_parents}

        folder = self.__db_folder_to_domain(
            db_folder,
            db_parents_dict,
        )

        return folder

    def get_root_folders(self, org_pk: int) -> list[Folder]:
        db_folders = FOL_Folder.objects.filter(
            org_id=org_pk, _parent=None, deleted=False
        )
        folders = list_map(
            db_folders,
            lambda f: self.__db_folder_to_domain(f, {}),
        )
        return folders

    def list_by_uuids(self, org_pk: int, uuids: list[UUID]) -> list[Folder]:
        db_folders = list(FOL_Folder.objects.filter(uuid__in=uuids, org_id=org_pk))
        pks = list_map(db_folders, lambda f: f.pk)
        closures = FOL_ClosureTable.objects.filter(child_id__in=pks).select_related(
            "parent"
        )
        db_parents = list_map(closures, lambda c: c.parent)
        db_parents_dict = {f.pk: f for f in db_parents}

        folders = list_map(
            db_folders, lambda f: self.__db_folder_to_domain(f, db_parents_dict)
        )
        return folders

    def get_dict(self, org_pk: int) -> dict[UUID, Folder]:
        folders = self.__as_id_dict(org_pk)

        domain_folders = {}
        for f in folders.values():
            domain_folders[f.uuid] = self.__db_folder_to_domain(f, folders)

        return domain_folders

    def get_list(self, org_pk: int) -> list[Folder]:
        folders = self.__as_id_dict(org_pk)

        folders_list = []
        for folder in folders.values():
            folders_list.append(self.__db_folder_to_domain(folder, folders))

        return folders_list

    def __get_closures_from_folder(
        self, folder: Folder, folder_pk: int
    ) -> list[FOL_ClosureTable]:
        parent_uuids = folder.parent_uuids
        ids = FOL_Folder.objects.filter(uuid__in=parent_uuids).values_list(
            "pk", flat=True
        )
        closures = list_map(
            ids, lambda id: FOL_ClosureTable(parent_id=id, child_id=folder_pk)
        )
        return closures

    def save(self, folder: Folder):
        assert folder.org_pk is not None
        db_folder = self.__db_folder_from_domain(folder)
        with transaction.atomic():
            db_folder.save()
            assert db_folder.pk is not None
            FOL_ClosureTable.objects.filter(child_id=db_folder.pk).delete()
            closures = self.__get_closures_from_folder(folder, db_folder.pk)
            FOL_ClosureTable.objects.bulk_create(closures)

    def delete(self, folder: Folder, repositories: list[ItemRepository]):
        assert folder.org_pk is not None
        f = self.__db_folder_from_domain(folder)
        for repo in repositories:
            repo.delete_items_of_folder(folder.uuid, folder.org_pk)
        f.deleted = True
        f.deleted_at = timezone.now()
        f.save()

    def get_children(self, org_pk: int, uuid: UUID) -> list[Folder]:
        db_folder = FOL_Folder.objects.filter(uuid=uuid, org_id=org_pk).get()
        closures = FOL_ClosureTable.objects.filter(
            child_id=db_folder.pk
        ).select_related("child")
        uuids = list_map(closures, lambda c: c.child.uuid)
        return self.list_by_uuids(org_pk, uuids)
