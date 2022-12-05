from typing import Optional, Type, Union, cast
from uuid import UUID, uuid4

from django.db import models
from django.db.models import QuerySet

from core.auth.models import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.upgrade import UpgradeRepository
from core.folders.domain.value_objects.keys import FolderKey
from core.folders.domain.value_objects.keys.parent_key import ParentKey
from core.rlc.models import Org
from core.seedwork.repository import RepositoryWarehouse


class FoldersFolder(models.Model):
    _parent = models.ForeignKey(
        "FoldersFolder", on_delete=models.CASCADE, null=True, blank=True
    )
    uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)
    name = models.CharField(max_length=1000)
    org = models.ForeignKey(
        Org, related_name="folders_folders", on_delete=models.CASCADE
    )
    keys = models.JSONField(blank=True)
    upgrades = models.JSONField(blank=True)
    stop_inherit = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "FoldersFolder"
        verbose_name_plural = "FoldersFolders"

    def __str__(self):
        return "foldersFolder: {};".format(self.pk)

    @property
    def parent(self) -> Optional[UUID]:
        if self._parent is None:
            return None
        return self._parent.uuid

    @staticmethod
    def query() -> QuerySet:
        return FoldersFolder.objects.all()

    @staticmethod
    def from_domain(folder: Folder) -> "FoldersFolder":
        keys = [k.as_dict() for k in folder.keys]
        upgrades = [u.as_dict() for u in folder.upgrades]

        parent_id: Optional[int] = None
        if folder.parent is not None:
            parent_id = FoldersFolder.from_domain(folder.parent).pk

        if FoldersFolder.objects.filter(uuid=folder.uuid).exists():
            f = FoldersFolder.objects.get(uuid=folder.uuid)
            f._parent_id = parent_id
            f.name = folder.name
            f.org_id = folder.org_pk
            f.keys = keys
            f.upgrades = upgrades
            f.stop_inherit = folder.stop_inherit

        else:
            f = FoldersFolder(
                _parent_id=parent_id,
                uuid=folder.uuid,
                name=folder.name,
                org_id=folder.org_pk,
                keys=keys,
                upgrades=upgrades,
                stop_inherit=folder.stop_inherit,
            )

        return f

    def to_domain(
        self, folders: dict[UUID, "FoldersFolder"], users: dict[UUID, RlcUser]
    ) -> Folder:
        # find the parent
        parent: Optional[Folder] = None
        if self.parent is not None:
            parent = folders[self.parent].to_domain(folders, users)

        # revive keys
        keys: list[Union[ParentKey, FolderKey]] = []
        for key in self.keys:
            if key["type"] == "FOLDER":
                owner = users[UUID(key["owner"])]
                fk = FolderKey.create_from_dict(key, owner)
                keys.append(fk)

            elif key["type"] == "PARENT":
                pk = ParentKey.create_from_dict(key)
                keys.append(pk)

        # revive folder
        folder = Folder(
            name=self.name,
            parent=parent,
            uuid=self.uuid,
            org_pk=self.org_id,
            keys=keys,
            stop_inherit=self.stop_inherit,
        )

        # revive upgrades
        for upgrade in self.upgrades:
            upgrade_repository = cast(
                Type[UpgradeRepository], RepositoryWarehouse.get(upgrade["repository"])
            )
            u = upgrade_repository.retrieve(uuid=upgrade["uuid"])
            folder.add_upgrade(u)

        # return
        return folder
