import mimetypes
from uuid import UUID

from django.http import FileResponse
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.data_sheets.api import schemas
from core.data_sheets.models import DataSheet, DataSheetTemplate
from core.data_sheets.models.data_sheet import DataSheetEncryptedFileEntry
from core.seedwork.api_layer import ApiError, Router

router = Router()


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
    sheet = (
        DataSheet.objects.prefetch_related(*DataSheet.ALL_PREFETCH_RELATED)
        .select_related("template")
        .filter(template__rlc_id=rlc_user.org_id)
        .filter(uuid=data.uuid)
        .first()
    )

    if not sheet:
        raise ApiError("Data Sheet not found.", status=404)

    if not sheet.has_access(rlc_user):
        raise ApiError("You have no access to this folder.")

    return {
        "id": sheet.pk,
        "name": sheet.name,
        "uuid": sheet.uuid,
        "folder_uuid": sheet.folder_uuid,
        "created": sheet.created,
        "updated": sheet.updated,
        "fields": sheet.template.get_fields_new(),
        "entries": sheet.get_entries_new(rlc_user),
        "template_name": sheet.template.name,
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
