from typing import cast
from uuid import UUID, uuid4

from django.db import models

from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.aggregates.upgrade import Item, Upgrade
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.domain.repositiories.upgrade import UpgradeRepository
from core.folders.domain.value_objects.keys import SymmetricKey
from core.folders.models import FoldersFolder
from core.seedwork.repository import RepositoryWarehouse


class DjangoRecordUpgradeRepository(UpgradeRepository):
    IDENTIFIER = "RECORD_UPGRADE"

    @classmethod
    def retrieve(cls, uuid: UUID) -> "RecordUpgrade":
        return RecordUpgrade.objects.get(uuid=uuid)


class RecordUpgrade(Upgrade, models.Model):
    REPOSITORY = DjangoRecordUpgradeRepository.IDENTIFIER

    uuid = models.UUIDField(unique=True, default=uuid4)
    raw_folder = models.ForeignKey(
        FoldersFolder, on_delete=models.CASCADE, related_name="record_upgrades"
    )

    class Meta:
        verbose_name = "RecordUpgrade"
        verbose_name_plural = "RecordUpgrades"

    def __str__(self):
        return "recordUpgrade: {};".format(self.pk)

    @property
    def folder(self) -> Folder:
        r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
        folder = r.retrieve(self.raw_folder.org_id, self.raw_folder.uuid)
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

    def set_folder(self, folder: Folder):
        self.raw_folder = FoldersFolder.from_domain(folder)

    def reencrypt(self, old_key: SymmetricKey, new_key: SymmetricKey):
        pass
