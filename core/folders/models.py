import uuid
from typing import Optional, Type, Union, cast

from django.db import models
from django.db.models import QuerySet

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.upgrade import UpgradeRepository
from core.folders.domain.value_objects.keys import FolderKey
from core.folders.domain.value_objects.keys.parent_key import ParentKey
from core.seedwork.repository import RepositoryWarehouse


class FoldersFolder(models.Model):
    _parent = models.ForeignKey("FoldersFolder", on_delete=models.CASCADE, null=True)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    name = models.CharField(max_length=1000)
    org_pk = models.IntegerField(null=True)
    keys = models.JSONField()
    upgrades = models.JSONField()

    class Meta:
        verbose_name = "FoldersFolder"
        verbose_name_plural = "FoldersFolders"

    def __str__(self):
        return "foldersFolder: {};".format(self.pk)

    @property
    def parent(self) -> Optional[uuid.UUID]:
        return self._parent_id

    @staticmethod
    def query() -> QuerySet:
        return FoldersFolder.objects.all()

    @staticmethod
    def from_domain(folder: Folder) -> "FoldersFolder":
        keys = [k.__dict__() for k in folder.keys]
        upgrades = [u.__dict__() for u in folder.upgrades]

        f = FoldersFolder(
            _parent_id=folder.parent_pk,
            pk=folder.pk,
            name=folder.name,
            org_pk=folder.org_pk,
            keys=keys,
            upgrades=upgrades,
        )

        return f

    def to_domain(self, folders: dict[uuid.UUID, "FoldersFolder"]) -> Folder:
        folder_repository = cast(
            Type[FolderRepository], RepositoryWarehouse.get(FolderRepository)
        )

        # find the parent
        parent: Optional[Folder] = None
        if self.parent is not None:
            parent = folders[self.parent].to_domain(folders)

        # revive keys
        keys: list[Union[ParentKey, FolderKey]] = []
        for key in self.keys:
            if key["type"] == "FOLDER":
                owner = folder_repository.find_key_owner(key["owner"])
                fk = FolderKey.create_from_dict(key, owner)
                keys.append(fk)

            elif key["type"] == "PARENT":
                pk = ParentKey.create_from_dict(key)
                keys.append(pk)

        # revive folder
        folder = Folder(
            name=self.name,
            parent=parent,
            pk=self.pk,
            org_pk=self.org_pk,
            keys=keys,
        )

        # revive upgrades
        for upgrade in self.upgrades:
            print(upgrade)
            upgrade_repository = cast(
                Type[UpgradeRepository], RepositoryWarehouse.get(upgrade["repository"])
            )
            u = upgrade_repository.create_from_dict(d=upgrade, folder=folder)
            folder.add_upgrade(u)

        # return
        return folder
