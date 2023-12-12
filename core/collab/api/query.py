from datetime import datetime
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
