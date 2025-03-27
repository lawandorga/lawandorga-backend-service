import mimetypes
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from pydantic import BaseModel

from core.auth.models import OrgUser
from core.data_sheets.api import schemas
from core.data_sheets.models import DataSheet, DataSheetTemplate
from core.data_sheets.models.data_sheet import DataSheetEncryptedFileEntry
from core.seedwork.api_layer import ApiError, Router

from seedwork.functional import list_map

router = Router()


@router.get(url="templates/", output_schema=list[schemas.OutputTemplate])
def query__templates(org_user: OrgUser):
    templates = DataSheetTemplate.objects.filter(org_id=org_user.org_id)
    return list(templates)


@router.get(
    url="templates/<int:id>/",
    output_schema=schemas.OutputTemplateDetail,
)
def query__template(org_user: OrgUser, data: schemas.InputTemplateDetail):
    return DataSheetTemplate.objects.get(org_id=org_user.org_id, id=data.id)


@router.get(
    url="<uuid:uuid>/",
    output_schema=schemas.OutputDataSheetDetail,
)
def query__data_sheet(org_user: OrgUser, data: schemas.InputQueryRecord):
    sheet = (
        DataSheet.objects.prefetch_related(*DataSheet.ALL_PREFETCH_RELATED)
        .select_related("template")
        .filter(template__org_id=org_user.org_id)
        .filter(uuid=data.uuid)
        .first()
    )

    if not sheet:
        raise ApiError("Data Sheet not found.", status=404)

    if not sheet.has_access(org_user):
        raise ApiError("You have no access to this folder.")

    return {
        "id": sheet.pk,
        "name": sheet.name,
        "uuid": sheet.uuid,
        "folder_uuid": sheet.folder_uuid,
        "created": sheet.created,
        "updated": sheet.updated,
        "fields": sheet.template.get_fields_new(),
        "entries": sheet.get_entries_new(org_user),
        "template_name": sheet.template.name,
    }


class InputFileEntryDownload(BaseModel):
    uuid: UUID
    record_id: int


@router.get(
    "file_entry_download/<int:record_id>/<uuid:uuid>/", output_schema=FileResponse
)
def query__download_file_entry(org_user: OrgUser, data: InputFileEntryDownload):
    try:
        entry = DataSheetEncryptedFileEntry.objects.get(
            record_id=data.record_id,
            field__uuid=data.uuid,
            field__template__org_id=org_user.org_id,
        )
    except ObjectDoesNotExist:
        raise ApiError(message="The file was not found.", status=404)
    file = entry.decrypt_file(user=org_user)
    response = FileResponse(file, content_type=mimetypes.guess_type(entry.file.name)[0])
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(
        entry.file.name
    )
    return response


class OutputDashboardRecord(BaseModel):
    folder_uuid: UUID
    uuid: UUID
    identifier: str
    state: str


@router.get("dashboard/", output_schema=list[OutputDashboardRecord])
def query__dashboard_page(org_user: OrgUser):
    recordsqs = DataSheet.objects.filter(template__rlc=org_user.org).prefetch_related(
        "state_entries", "users_entries", "users_entries__value"
    )
    records = list(recordsqs)
    records_data = []
    for record in records:
        users_entries = list(record.users_entries.all())
        if len(users_entries) <= 0:
            continue

        user_entry = users_entries[0]
        user_ids = list_map(list(user_entry.value.all()), lambda x: x.pk)
        if org_user.pk not in user_ids:
            continue

        state_entries = list(record.state_entries.all())
        if len(state_entries) <= 0:
            continue
        state_entry = state_entries[0]
        if state_entry.value != "Open":
            continue

        records_data.append(
            {
                "uuid": record.uuid,
                "folder_uuid": record.folder_uuid,
                "identifier": record.identifier,
                "state": "Open",
            }
        )

    return records_data
