import mimetypes
from dataclasses import dataclass
from uuid import UUID

from django.http import FileResponse
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.data_sheets.api import schemas
from core.data_sheets.models import DataSheet, DataSheetTemplate
from core.data_sheets.models.data_sheet import DataSheetEncryptedFileEntry
from core.data_sheets.use_cases.record import migrate_record_into_folder
from core.permissions.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from core.seedwork.api_layer import ApiError, Router

router = Router()


@dataclass
class SheetMigrate:
    sheet: DataSheet
    current_user: OrgUser
    SHOW: bool

    @property
    def name(self) -> str:
        return self.sheet.name

    @property
    def uuid(self) -> UUID:
        return self.sheet.uuid

    @property
    def token(self) -> str:
        if "Token" in self.sheet.attributes:
            return str(self.sheet.attributes["Token"])
        return "-"

    @property
    def attributes(self) -> dict:
        if self.SHOW or self.current_user.uuid in map(
            lambda x: x["uuid"], self.persons_with_access
        ):
            return self.sheet.attributes
        return {}

    @property
    def persons_with_access(self) -> list:
        return [
            {"name": e.user.name, "uuid": e.user.uuid}
            for e in list(self.sheet.encryptions.all())
        ]


@router.get(url="non_migrated/", output_schema=list[schemas.OutputNonMigratedDataSheet])
def query__non_migrated(rlc_user: OrgUser):
    sheets_1 = list(
        DataSheet.objects.filter(template__rlc_id=rlc_user.org_id)
        .filter(folder_uuid=None)
        .prefetch_related(*DataSheet.UNENCRYPTED_PREFETCH_RELATED, "encryptions__user")
        .select_related("template")
    )

    show = rlc_user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    sheets_2 = [
        SheetMigrate(sheet=s, current_user=rlc_user, SHOW=show) for s in sheets_1
    ]

    return sheets_2


@router.get(url="templates/", output_schema=list[schemas.OutputTemplate])
def query__templates(rlc_user: OrgUser):
    templates = DataSheetTemplate.objects.filter(rlc_id=rlc_user.org_id)
    return list(templates)


@router.get(
    url="templates/<int:id>/",
    output_schema=schemas.OutputTemplateDetail,
)
def query__template(rlc_user: OrgUser, data: schemas.InputTemplateDetail):
    return DataSheetTemplate.objects.get(rlc_id=rlc_user.org_id, id=data.id)


@router.get(
    url="<uuid:uuid>/",
    output_schema=schemas.OutputDataSheetDetail,
)
def query__data_sheet(rlc_user: OrgUser, data: schemas.InputQueryRecord):
    record = (
        DataSheet.objects.prefetch_related(*DataSheet.ALL_PREFETCH_RELATED)
        .select_related("old_client", "template")
        .filter(template__rlc_id=rlc_user.org_id)
        .get(uuid=data.uuid)
    )

    if not record.has_access(rlc_user):
        raise ApiError("You have no access to this folder.")

    if not record.folder_uuid:
        migrate_record_into_folder(rlc_user, record)

    return {
        "id": record.pk,
        "name": record.name,
        "uuid": record.uuid,
        "folder_uuid": record.folder_uuid,
        "created": record.created,
        "updated": record.updated,
        "fields": record.template.get_fields_new(),
        "entries": record.get_entries_new(rlc_user),
        "template_name": record.template.name,
    }


class InputFileEntryDownload(BaseModel):
    uuid: UUID
    record_id: int


@router.get(
    "file_entry_download/<int:record_id>/<uuid:uuid>/", output_schema=FileResponse
)
def query__download_file_entry(rlc_user: OrgUser, data: InputFileEntryDownload):
    entry = DataSheetEncryptedFileEntry.objects.get(
        record_id=data.record_id,
        field__uuid=data.uuid,
        field__template__rlc_id=rlc_user.org_id,
    )
    file = entry.decrypt_file(user=rlc_user)
    response = FileResponse(file, content_type=mimetypes.guess_type(entry.file.name)[0])
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(
        entry.file.name
    )
    return response
