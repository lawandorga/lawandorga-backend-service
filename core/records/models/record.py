from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from django.db import models

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository
from core.folders.infrastructure.folder_addon import FolderAddon
from core.rlc.models import Org
from core.seedwork.aggregate import Aggregate
from core.seedwork.events_addon import EventsAddon


class RecordRepository(ItemRepository):
    IDENTIFIER = "RECORDS_RECORD"

    def retrieve(self, uuid: UUID, org_pk: Optional[int] = None) -> "RecordsRecord":
        assert isinstance(uuid, UUID), f"uuid must be a UUID but is {type(uuid)}"
        assert isinstance(org_pk, int), f"org_pk must be an int but is {type(org_pk)}"
        return RecordsRecord.objects.filter(uuid=uuid, org_id=org_pk).get()

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        _org_id = org_pk if org_pk else 0
        RecordsRecord.objects.filter(folder_uuid=folder_uuid, org_id=_org_id).delete()


class RecordsRecord(Aggregate, models.Model):
    REPOSITORY = RecordRepository.IDENTIFIER

    @classmethod
    def create(cls, token: str, user: OrgUser, folder: Folder, pk=0) -> "RecordsRecord":
        record = RecordsRecord(name=token, org=user.org)
        if pk:
            record.pk = pk
        record.folder.put_obj_in_folder(folder)
        return record

    name = models.CharField(max_length=200)
    org = models.ForeignKey(
        Org, related_name="records_records", on_delete=models.CASCADE
    )
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid4)
    folder_uuid = models.UUIDField(db_index=True)
    is_archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    addons = dict(events=EventsAddon, folder=FolderAddon)

    if TYPE_CHECKING:
        events: EventsAddon
        folder: FolderAddon

    class Meta:
        verbose_name = "Records-Record"
        verbose_name_plural = "Records-Records"

    def __str__(self):
        return "recordsRecord: {}; token: {}; org: {};".format(
            self.uuid, self.token, self.org_pk
        )

    @property
    def org_pk(self) -> int:
        return self.org.pk

    @property
    def token(self) -> str:
        return self.name

    def change_token(self, token: str):
        self.name = token
        self.folder.obj_renamed()
