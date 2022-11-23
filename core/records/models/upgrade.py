import uuid
from typing import cast
from uuid import UUID

from django.core.cache import cache
from django.db import models

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.upgrade import Item, Upgrade
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.upgrade import UpgradeRepository
from core.folders.domain.value_objects.keys import SymmetricKey
from core.seedwork.repository import RepositoryWarehouse


class RecordUpgradeRepository(UpgradeRepository):
    IDENTIFIER = "RECORD_UPGRADE"

    @classmethod
    def retrieve(cls, pk: UUID) -> "RecordUpgrade":
        return RecordUpgrade.objects.get(pk=pk)


class RecordUpgrade(Upgrade, models.Model):
    REPOSITORY = RecordUpgradeRepository.IDENTIFIER

    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    org_pk = models.IntegerField()
    folder_pk = models.UUIDField()

    class Meta:
        verbose_name = "RecordUpgrade"
        verbose_name_plural = "RecordUpgrades"

    def __str__(self):
        return "recordUpgrade: {};".format(self.pk)

    @property
    def folder(self) -> Folder:
        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
        folder = r.retrieve(self.org_pk, self.folder_pk)
        return folder

    @property
    def content(self) -> list[Item]:
        records_1 = list(self.records.all())
        records_2 = map(
            lambda x: Item(x.identifier, {"OPEN": "/records/{}/".format(x.pk)}),
            records_1,
        )
        records_3 = list(records_2)
        return records_3

    def get_folders(self):
        place = "core/records/models/upgrade/get_folders"
        folders = cache.get(place, None)
        if folders is None:
            r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
            folders = r.dict(self.org_pk)

    def reencrypt(self, old_key: SymmetricKey, new_key: SymmetricKey):
        pass
