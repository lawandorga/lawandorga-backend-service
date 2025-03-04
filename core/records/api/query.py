import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from pydantic import BaseModel, ConfigDict, field_validator

from core.auth.models import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.records.models.access import RecordsAccessRequest
from core.records.models.deletion import RecordsDeletion
from core.records.models.record import Pagination, RecordRepository, RecordsRecord
from core.records.models.record import Search as RrSearch
from core.records.models.setting import RecordsView
from core.seedwork.api_layer import Router

from seedwork.functional import list_map

router = Router()


@dataclass
class RecordDataPoint:
    record: RecordsRecord
    folder: Folder

    @property
    def folder_uuid(self) -> UUID:
        return self.folder.uuid

    @property
    def attributes(self) -> dict:
        return json.loads(self.record.attributes)

    def has_access(self, user: OrgUser) -> bool:
        return self.folder.has_access(user)

    @property
    def token(self) -> str:
        return self.record.token

    @property
    def data_sheet_uuid(self) -> Optional[UUID]:
        uuids = self.attributes.get("sheet_uuids", [])
        if len(uuids) == 0:
            return None
        return UUID(uuids[0])


class OutputRecord(BaseModel):
    uuid: UUID
    token: str
    attributes: dict[str, str | list[str]]
    has_access: bool
    folder_uuid: UUID
    data_sheet_uuid: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


class OutputRecordsPage(BaseModel):
    records: list[OutputRecord]
    total: int


class QueryInput(BaseModel):
    limit: int
    offset: int
    token: str | None = None
    year: int | None = None
    general: str | None = None
    order_by: str | None = None

    @field_validator("year", mode="before")
    def year_to_none(cls, v):
        try:
            val = int(v)
        except ValueError:
            return None
        if val < 0:
            return 0
        return val


@router.get(url="dashboard/", output_schema=OutputRecordsPage)
def query__records_page(org_user: OrgUser, data: QueryInput):
    rr = RecordRepository()
    fr = DjangoFolderRepository()

    records, total = rr.list(
        org_user.org_id,
        RrSearch(token=data.token, year=data.year, general=data.general),
        Pagination(limit=data.limit, offset=data.offset),
        data.order_by,
    )
    folder_uuids = list_map(records, lambda r: r.folder_uuid)

    foldersl = fr.list_by_uuids(org_user.org_id, folder_uuids)
    folders = {f.uuid: f for f in foldersl}

    points = [RecordDataPoint(r, folders[r.folder_uuid]) for r in records]

    records_2 = [
        {
            "uuid": p.record.uuid,
            "token": p.token,
            "folder_uuid": p.folder_uuid,
            "attributes": p.attributes,
            "has_access": p.has_access(org_user),
            "data_sheet_uuid": p.data_sheet_uuid,
        }
        for p in points
    ]

    return {
        "records": records_2,
        "total": total,
    }


class OutputView(BaseModel):
    name: str
    columns: list[str]
    uuid: UUID
    shared: bool
    ordering: int

    model_config = ConfigDict(from_attributes=True)


class OutputDeletion(BaseModel):
    created: datetime
    explanation: str
    uuid: UUID
    processed_by_detail: str
    record_detail: str
    requested_by_detail: str
    state: str
    processed: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class OutputAccessRequest(BaseModel):
    created: datetime
    uuid: UUID
    processed_by_detail: str
    requested_by_detail: str
    record_detail: str
    state: str
    processed_on: Optional[datetime]
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class OutputBadges(BaseModel):
    deletion_requests: int
    access_requests: int


class OutputInfos(BaseModel):
    deletions: list[OutputDeletion]
    access_requests: list[OutputAccessRequest]
    badges: OutputBadges
    views: list[OutputView]


@router.get(url="infos/", output_schema=OutputInfos)
def query_infos(user: OrgUser):
    deletions = RecordsDeletion.objects.filter(
        Q(requestor__org_id=user.org_id)
        | Q(processor__org_id=user.org_id)
        | Q(record__org_id=user.org_id)
    ).select_related("requestor__user", "processor__user", "record")

    access_requests = RecordsAccessRequest.objects.filter(
        Q(requestor__org_id=user.org_id)
        | Q(processor__org_id=user.org_id)
        | Q(record__org_id=user.org_id)
    ).select_related("requestor__user", "processor__user", "record")

    badges = {
        "deletion_requests": deletions.filter(state="re").count(),
        "access_requests": access_requests.filter(state="re").count(),
    }

    views = list(RecordsView.objects.filter(Q(org_id=user.org_id) | Q(user=user)))

    return {
        "deletions": list(deletions),
        "access_requests": list(access_requests),
        "badges": badges,
        "views": views,
    }


class OutputDashboardChangedRecord(BaseModel):
    folder_uuid: UUID
    uuid: UUID
    identifier: str
    updated: datetime


@router.get("dashboard/changed/", output_schema=list[OutputDashboardChangedRecord])
def changed_records_information(org_user: OrgUser):
    recordsqs = RecordsRecord.objects.filter(
        org_id=org_user.org_id, updated__gt=timezone.now() - timedelta(days=10)
    )
    records = list(recordsqs)
    folder_uuids = list_map(records, lambda x: x.folder_uuid)
    r = DjangoFolderRepository()
    foldersl = r.list_by_uuids(org_pk=org_user.org_id, uuids=folder_uuids)
    folders = {folder.uuid: folder for folder in foldersl}

    changed_records_data = []
    for record in records:
        folder = folders[record.folder_uuid]
        if not folder.has_access(org_user):
            continue

        changed_records_data.append(
            {
                "uuid": record.uuid,
                "folder_uuid": folder.uuid,
                "identifier": record.name,
                "updated": record.updated,
            }
        )

    return changed_records_data
