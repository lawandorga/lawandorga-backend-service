import mimetypes
from datetime import datetime
from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.seedwork.api_layer import Router
from core.upload.models import UploadLink


class InputQueryLink(BaseModel):
    uuid: UUID


class InputDownloadFile(BaseModel):
    file: UUID
    link: UUID


class OutputUploadFile(BaseModel):
    name: str
    uuid: UUID
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class OutputQueryLink(BaseModel):
    uuid: UUID
    name: str
    link: str
    created: datetime
    disabled: bool
    files: list[OutputUploadFile]

    model_config = ConfigDict(from_attributes=True)


class OutputQueryLinkPublic(BaseModel):
    uuid: UUID
    name: str
    link: str
    created: datetime
    disabled: bool

    model_config = ConfigDict(from_attributes=True)


router = Router()


@router.get(
    url="<uuid:uuid>/",
    output_schema=OutputQueryLink,
)
def query__link(org_user: OrgUser, data: InputQueryLink):
    link = get_object_or_404(UploadLink, org_id=org_user.org_id, uuid=data.uuid)
    return {
        "uuid": link.uuid,
        "name": link.name,
        "link": link.link,
        "created": link.created,
        "disabled": link.disabled,
        "files": list(link.files.all()),
    }


@router.get(
    url="<uuid:uuid>/public/",
    output_schema=OutputQueryLinkPublic,
)
def query__link_public(anonymous_user: AnonymousUser, data: InputQueryLink):
    link = get_object_or_404(UploadLink, uuid=data.uuid)
    return link


@router.get(
    url="<uuid:link>/<uuid:file>/",
    output_schema=FileResponse,
)
def query__download_file(org_user: OrgUser, data: InputDownloadFile):
    link = get_object_or_404(UploadLink, org_id=org_user.org_id, uuid=data.link)

    filename, file = link.download(data.file, org_user)

    response = FileResponse(
        file, filename=filename, content_type=mimetypes.guess_type(filename)[0]
    )
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
    return response
