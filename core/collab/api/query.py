import io
from datetime import datetime
from typing import Optional
from uuid import UUID

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.template import loader
from pydantic import BaseModel, ConfigDict
from weasyprint import HTML

from core.auth.models.org_user import OrgUser
from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead
from core.collab.models.template import Template
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


class OutputLetterhead(BaseModel):
    uuid: UUID
    address_line_1: str
    address_line_2: str
    address_line_3: str
    address_line_4: str
    address_line_5: str
    text_right: str
    logo_base64: str

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="letterhead/<uuid:uuid>/",
    output_schema=OutputLetterhead,
)
def query__letterhead(org_user: OrgUser, data: InputUuid):
    letterhead = Letterhead.objects.get(uuid=data.uuid, org=org_user.org)
    return letterhead


class OutputFooter(BaseModel):
    uuid: UUID
    column_1: str
    column_2: str
    column_3: str
    column_4: str

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="footer/<uuid:uuid>/",
    output_schema=OutputFooter,
)
def query__footer(org_user: OrgUser, data: InputUuid):
    footer = Footer.objects.get(uuid=data.uuid, org=org_user.org)
    return footer


class OutputTemplate(BaseModel):
    uuid: UUID
    name: str
    description: str
    letterhead: OutputLetterhead | None
    footer: OutputFooter | None
    template_type: str = "deprecated"

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


@router.get(
    url="templates/",
    output_schema=list[OutputTemplate],
)
def query__templates(org_user: OrgUser):
    return list(Template.objects.filter(org=org_user.org))


@router.get(
    url="template/<uuid:uuid>/",
    output_schema=OutputTemplate,
)
def query__template(org_user: OrgUser, data: InputUuid):
    template = Template.objects.get(uuid=data.uuid, org=org_user.org)
    return template


class InputPdf(BaseModel):
    uuid: UUID
    debug: bool = False


@router.get(
    url="<uuid:uuid>/pdf/",
    output_schema=HttpResponse | FileResponse,
)
def query__collab_pdf(org_user: OrgUser, data: InputPdf):
    cr = CollabRepository()
    fr = DjangoFolderRepository()
    collab = cr.get_document(data.uuid, org_user, fr)
    header = collab.template.letterhead if collab.template else None
    footer = collab.template.footer if collab.template else None
    html = loader.render_to_string(
        "collab/templates/pdf.html",
        context={"collab": collab, "header": header, "footer": footer},
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


@router.get(
    url="template/<uuid:uuid>/pdf/",
    output_schema=HttpResponse | FileResponse,
)
def query__collab_template_pdf(org_user: OrgUser, data: InputPdf):
    template = Template.objects.select_related("letterhead", "footer").get(
        uuid=data.uuid, org=org_user.org
    )
    html = loader.render_to_string(
        "collab/templates/template.html",
        context={
            "template": template,
            "header": template.letterhead,
            "footer": template.footer,
        },
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
        filename=f"{template.name}.pdf",
    )
    return response


class OutputCollab(BaseModel):
    uuid: UUID
    name: str
    text: str
    password: str
    created_at: datetime
    history: list[OutputDocument]
    template: Optional[OutputTemplate]

    model_config = ConfigDict(from_attributes=True)


@router.get(
    url="<uuid:uuid>/",
    output_schema=OutputCollab,
)
def query__data_sheet(org_user: OrgUser, data: InputUuid):
    cr = CollabRepository()
    fr = DjangoFolderRepository()
    collab = cr.get_document(data.uuid, org_user, fr)
    return collab
