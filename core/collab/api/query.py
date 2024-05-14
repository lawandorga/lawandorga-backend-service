from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import OrgUser
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
    type: Literal["footer", "letterhead"]


@router.get(
    url="templates/",
    output_schema=list[OutputTemplate],
)
def query__templates(rlc_user: OrgUser):
    return []


class OutputLetterhead(BaseModel):
    pass


@router.get(
    url="letterhead/<uuid:uuid>/",
    output_schema=OutputLetterhead,
)
def query__letterhead(rlc_user: OrgUser, data: InputUuid):
    return {}


class OutputFooter(BaseModel):
    pass


@router.get(
    url="footer/<uuid:uuid>/",
    output_schema=OutputFooter,
)
def query__footer(rlc_user: OrgUser, data: InputUuid):
    return {}
