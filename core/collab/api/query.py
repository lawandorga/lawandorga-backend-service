import io
from datetime import datetime
from typing import Literal
from uuid import UUID

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.template import loader
from pydantic import BaseModel, ConfigDict
from weasyprint import HTML

from core.auth.models.org_user import OrgUser
from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead
from core.collab.repositories.collab import CollabRepository
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork.api_layer import Router

router = Router()


class InputUuid(BaseModel):
    uuid: UUID


class OutputDocument(BaseModel):
    user: str
    text: str
    time: datetime

    model_config = ConfigDict(from_attributes=True)


class OutputCollab(BaseModel):
    uuid: UUID
    name: str
    text: str
    password: str
    created_at: datetime
    history: list[OutputDocument]

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="<uuid:uuid>/",
    output_schema=OutputCollab,
)
def query__data_sheet(rlc_user: OrgUser, data: InputUuid):
    cr = CollabRepository()
    fr = DjangoFolderRepository()
    collab = cr.get_document(data.uuid, rlc_user, fr)
    return collab


class OutputTemplate(BaseModel):
    uuid: UUID
    name: str
    description: str
    template_type: Literal["footer", "letterhead"]

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="templates/",
    output_schema=list[OutputTemplate],
)
def query__templates(rlc_user: OrgUser):
    lhs = Letterhead.objects.filter(org=rlc_user.org)
    footer = Footer.objects.filter(org=rlc_user.org)
    return [*lhs, *footer]


class OutputLetterhead(BaseModel):
    uuid: UUID
    name: str
    description: str
    address_line_1: str
    address_line_2: str
    address_line_3: str
    address_line_4: str
    address_line_5: str
    text_right: str

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="letterhead/<uuid:uuid>/",
    output_schema=OutputLetterhead,
)
def query__letterhead(rlc_user: OrgUser, data: InputUuid):
    lh = Letterhead.objects.get(uuid=data.uuid, org=rlc_user.org)
    return lh


class OutputFooter(BaseModel):
    uuid: UUID
    name: str
    description: str
    column_1: str
    column_2: str
    column_3: str
    column_4: str

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="footer/<uuid:uuid>/",
    output_schema=OutputFooter,
)
def query__footer(rlc_user: OrgUser, data: InputUuid):
    footer = Footer.objects.get(uuid=data.uuid, org=rlc_user.org)
    return footer


class InputPdf(BaseModel):
    uuid: UUID
    debug: bool = False


@router.get(
    url="<uuid:uuid>/pdf/",
    output_schema=HttpResponse | FileResponse,
)
def query__collab_pdf(rlc_user: OrgUser, data: InputPdf):
    cr = CollabRepository()
    fr = DjangoFolderRepository()
    collab = cr.get_document(data.uuid, rlc_user, fr)
    html = loader.render_to_string(
        "collab/templates/pdf.html", context={"collab": collab}
    )

    if data.debug:
        return HttpResponse(html, content_type="text/html")

    htmldoc = HTML(string=html, base_url=settings.MAIN_BACKEND_URL)
    buffer = io.BytesIO()
    htmldoc.write_pdf(buffer)
    buffer.seek(0)
    response = FileResponse(
        buffer,
        as_attachment=False,
        content_type="application/pdf",
        filename=f"{collab.name}.pdf",
    )
    return response
