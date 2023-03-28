import itertools
from dataclasses import dataclass
from typing import Optional, cast
from uuid import UUID

from django.db.models import Q

from core.auth.models import RlcUser
from core.data_sheets.models import Record, RecordTemplate
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositiories.folder import FolderRepository
from core.records.helpers import merge_attrs
from core.records.models.access import RecordsAccessRequest
from core.records.models.deletion import RecordsDeletion
from core.records.models.record import RecordsRecord
from core.records.models.setting import RecordsView
from core.seedwork.api_layer import Router
from core.seedwork.repository import RepositoryWarehouse

from . import schemas

router = Router()


@dataclass
class RecordDataPoint:
    record: RecordsRecord
    folder: Folder
    ALL_DATA_SHEETS: list[Record]

    @property
    def data_sheets(self) -> list[Record]:
        return [ds for ds in self.ALL_DATA_SHEETS if ds.folder_uuid == self.folder.uuid]

    @property
    def folder_uuid(self) -> UUID:
        return self.folder.uuid

    @property
    def attributes(self) -> dict:
        attrs: dict = {}
        for ds in self.data_sheets:
            attrs = merge_attrs(attrs, ds.attributes)
        return attrs

    def has_access(self, user: RlcUser) -> bool:
        return self.folder.has_access(user)

    @property
    def delete_requested(self) -> bool:
        return False

    @property
    def token(self) -> str:
        return self.record.token

    @property
    def data_sheet_uuid(self) -> Optional[UUID]:
        return self.data_sheets[0].uuid if self.data_sheets else None


@router.get(url="dashboard/", output_schema=schemas.OutputRecordsPage)
def query__records_page(rlc_user: RlcUser):
    records_1 = list(RecordsRecord.objects.filter(org_id=rlc_user.org_id))
    data_sheets_1 = list(
        Record.objects.filter(template__rlc_id=rlc_user.org_id)
        .prefetch_related(*Record.UNENCRYPTED_PREFETCH_RELATED)
        .select_related("template")
    )
    r = cast(FolderRepository, RepositoryWarehouse.get(FolderRepository))
    folders = r.get_dict(rlc_user.org_id)

    points_1 = [
        RecordDataPoint(r, folders[r.folder_uuid], data_sheets_1) for r in records_1
    ]

    records_2 = [
        {
            "uuid": p.record.uuid,
            "token": p.token,
            "folder_uuid": p.folder_uuid,
            "attributes": p.attributes,
            "delete_requested": p.delete_requested,
            "has_access": p.has_access(rlc_user),
            "data_sheet_uuid": p.data_sheet_uuid,
        }
        for p in points_1
    ]

    columns_1 = list(
        RecordTemplate.objects.filter(rlc_id=rlc_user.org_id).values_list(
            "show", flat=True
        )
    )
    columns_2 = itertools.chain(*columns_1)
    columns_3 = list(dict.fromkeys(columns_2))

    views = list(
        RecordsView.objects.filter(Q(org_id=rlc_user.org_id) | Q(user=rlc_user))
    )

    deletions = RecordsDeletion.objects.filter(
        Q(requestor__org_id=rlc_user.org_id)
        | Q(processor__org_id=rlc_user.org_id)
        | Q(record__org_id=rlc_user.org_id)
    )

    access_requests = RecordsAccessRequest.objects.filter(
        Q(requestor__org_id=rlc_user.org_id)
        | Q(processor__org_id=rlc_user.org_id)
        | Q(record__org_id=rlc_user.org_id)
    )

    badges = {
        "deletion_requests": deletions.filter(state="re").count(),
        "access_requests": access_requests.filter(state="re").count(),
    }

    return {
        "columns": columns_3,
        "records": records_2,
        "views": views,
        "deletions": list(deletions),
        "access_requests": list(access_requests),
        "badges": badges,
    }
