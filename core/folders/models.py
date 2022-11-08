import uuid
from typing import Type, cast

from django.db import models
from django.db.models import QuerySet

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.upgrade import Upgrade
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.upgrade import UpgradeRepository
from core.folders.domain.value_objects.keys import FolderKey
from core.seedwork.repository import RepositoryWarehouse


class FoldersFolder(models.Model):
    parent = models.UUIDField(null=True)
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

    @staticmethod
    def query() -> QuerySet:
        return FoldersFolder.objects.all()

    @staticmethod
    def from_domain(folder: Folder) -> "FoldersFolder":
        print([k.key.origin for k in folder.keys])
        keys = [k.__dict__() for k in folder.keys]
        upgrades = [u.__dict__() for u in folder.upgrades]

        f = FoldersFolder(
            parent=folder.parent,
            pk=folder.pk,
            name=folder.name,
            org_pk=folder.org_pk,
            keys=keys,
            upgrades=upgrades,
        )

        return f

    def to_domain(self) -> Folder:
        keys = []
        folder_repository = cast(
            Type[FolderRepository], RepositoryWarehouse.get(FolderRepository)
        )
        for key in self.keys:
            owner = folder_repository.find_key_owner(key['owner'])
            k = FolderKey.create_from_dict(key, owner)
            keys.append(k)

        upgrades = []
        for upgrade in self.upgrades:
            upgrade_repository = cast(
                Type[UpgradeRepository], RepositoryWarehouse.get(upgrade.repository)
            )
            loaded_upgrade = upgrade_repository.load_upgrade(upgrade['upgrade_pk'])
            u = Upgrade.create_from_dict(upgrade, loaded_upgrade)
            upgrades.append(u)

        f = Folder(
            name=self.name, pk=self.pk, org_pk=self.org_pk, keys=keys, upgrades=upgrades
        )

        return f
