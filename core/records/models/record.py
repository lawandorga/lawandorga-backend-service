import json
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from django.db import models
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository
from core.folders.infrastructure.folder_addon import FolderAddon
from core.records.helpers import merge_attrs
from core.rlc.models import Org
from core.seedwork.aggregate import Aggregate
from core.seedwork.events_addon import EventsAddon

if TYPE_CHECKING:
    from core.data_sheets.models import DataSheet


class Pagination(BaseModel):
    limit: int = 10
    offset: int = 0

    @property
    def start(self):
        return self.offset

    @property
    def end(self):
        return self.limit


class Search(BaseModel):
    token: str | None = None
    year: int | None = None
    general: str | None = None


class RecordRepository(ItemRepository):
    IDENTIFIER = "RECORDS_RECORD"

    def retrieve(self, uuid: UUID, org_pk: Optional[int] = None) -> "RecordsRecord":
        assert isinstance(uuid, UUID), f"uuid must be a UUID but is {type(uuid)}"
        assert isinstance(org_pk, int), f"org_pk must be an int but is {type(org_pk)}"
        return RecordsRecord.objects.filter(uuid=uuid, org_id=org_pk).get()

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        _org_id = org_pk if org_pk else 0
        RecordsRecord.objects.filter(folder_uuid=folder_uuid, org_id=_org_id).delete()

    def list(
        self, org_pk: int, search: Search, pagination: Pagination
    ) -> tuple[list["RecordsRecord"], int]:
        records = RecordsRecord.objects.filter(org_id=org_pk)
        if search.token:
            records = records.filter(name__icontains=search.token)
        if search.year:
            records = records.filter(created__year=search.year)
        if search.general:
            records = records.filter(attributes__icontains=search.general)

        filtered_count = records.count()
        records = records.order_by("-created")
        if pagination:
            records = records[pagination.start : pagination.end]
        return list(records), filtered_count


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
    attributes = models.TextField(default="{}")

    addons = dict(events=EventsAddon, folder=FolderAddon)

    if TYPE_CHECKING:
        events: EventsAddon
        folder: FolderAddon
        org_id: int

    class Meta:
        verbose_name = "Records-Record"
        verbose_name_plural = "Records-Records"

    def __str__(self):
        return "recordsRecord: {}; token: {}; org: {};".format(
            self.uuid, self.token, self.org_pk
        )

    @property
    def org_pk(self) -> int:
        return self.org_id

    @property
    def token(self) -> str:
        return self.name

    def change_token(self, token: str):
        self.name = token
        self.folder.obj_renamed()

    def set_attributes(self, data_sheets: list["DataSheet"]) -> None:
        attrs: dict = {}
        attrs["sheet_uuids"] = [str(ds.uuid) for ds in data_sheets]
        for ds in data_sheets:
            assert ds.folder_uuid == self.folder_uuid
            attrs = merge_attrs(attrs, ds.attributes)
        attrs["Created"] = self.created.strftime("%d.%m.%Y %H:%M:%S")
        attrs["Updated"] = self.updated.strftime("%d.%m.%Y %H:%M:%S")
        self.attributes = json.dumps(attrs)
