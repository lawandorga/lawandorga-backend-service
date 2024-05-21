from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import OrgUser
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
    # TODO: add the footers as well
    return [*lhs]


class OutputLetterhead(BaseModel):
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
    pass


@router.get(
    url="footer/<uuid:uuid>/",
    output_schema=OutputFooter,
)
def query__footer(rlc_user: OrgUser, data: InputUuid):
    return {}
