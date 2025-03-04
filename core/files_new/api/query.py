import mimetypes
from datetime import datetime
from uuid import UUID

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.files_new.models import EncryptedRecordDocument
from core.seedwork.api_layer import ApiError, Router


class InputQueryFile(BaseModel):
    uuid: UUID


class OutputFile(BaseModel):
    uuid: UUID
    name: str
    created: datetime
    updated: datetime

    model_config = ConfigDict(from_attributes=True)


router = Router()


@router.get(
    url="<uuid:uuid>/download/",
    output_schema=FileResponse,
)
def query__download_file(rlc_user: OrgUser, data: InputQueryFile):
    f = get_object_or_404(
        EncryptedRecordDocument, org_id=rlc_user.org_id, uuid=data.uuid
    )

    try:
        file = f.download(rlc_user)
    except FileNotFoundError:
        raise ApiError(
            "The file could not be found on the server. "
            "Please delete it or contact it@law-orga.de "
            "to have it recovered."
        )

    response = FileResponse(file, content_type=mimetypes.guess_type(f.name)[0])
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(f.name)
    return response


@router.get(
    url="<uuid:uuid>/",
    output_schema=OutputFile,
)
def query__retrieve_file(rlc_user: OrgUser, data: InputQueryFile):
    f = get_object_or_404(
        EncryptedRecordDocument, org_id=rlc_user.org_id, uuid=data.uuid
    )
    return f
