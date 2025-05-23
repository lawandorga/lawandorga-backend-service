import json
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from django.db import models
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.item import ItemRepository
from core.folders.infrastructure.item_mixins import FolderItemMixin
from core.org.models import Org
from core.records.helpers import merge_attrs
from core.seedwork.domain_layer import DomainError
from messagebus.domain.collector import EventCollector

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

    def delete_items_of_folder(self, folder_uuid: UUID, org_pk: int | None) -> None:
        _org_id = org_pk if org_pk else 0
        RecordsRecord.objects.filter(folder_uuid=folder_uuid, org_id=_org_id).delete()

    def list(
        self,
        org_pk: int,
        search: Search,
        pagination: Pagination,
        order_by: str | None = "-created",
    ) -> tuple[list["RecordsRecord"], int]:
        if order_by is None:
            order_by = "-created"
        records = RecordsRecord.objects.filter(org_id=org_pk)
        if search.token:
            records = records.filter(name__icontains=search.token)
        if search.year:
            if search.year < 1900 or search.year > 2100:
                raise DomainError("Year must be between 1900 and 2100")
            records = records.filter(created__year=search.year)
        if search.general:
            records = records.filter(attributes__icontains=search.general)

        filtered_count = records.count()
        records = records.order_by(order_by)
        if pagination:
            records = records[pagination.start : pagination.end]
        return list(records), filtered_count


class RecordsRecord(FolderItemMixin, models.Model):
    REPOSITORY = RecordRepository.IDENTIFIER

    @classmethod
    def create(
        cls, token: str, user: OrgUser, folder: Folder, collector: EventCollector, pk=0
    ) -> "RecordsRecord":
        record = RecordsRecord(name=token, org=user.org)
        if pk:
            record.pk = pk
        record.put_into_folder(folder, collector)
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

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "REC_RecordsRecord"
        verbose_name_plural = "REC_RecordsRecords"

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

    def change_token(self, token: str, collector: EventCollector) -> None:
        self.name = token
        self.renamed(collector)

    def set_attributes(self, data_sheets: list["DataSheet"]) -> None:
        attrs: dict = {}
        attrs["sheet_uuids"] = [str(ds.uuid) for ds in data_sheets]
        for ds in data_sheets:
            assert ds.folder_uuid == self.folder_uuid
            attrs = merge_attrs(attrs, ds.attributes)
        attrs["Created"] = self.created.strftime("%d.%m.%Y %H:%M:%S")
        attrs["Updated"] = self.updated.strftime("%d.%m.%Y %H:%M:%S")
        self.attributes = json.dumps(attrs)
