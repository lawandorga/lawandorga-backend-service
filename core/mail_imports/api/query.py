from uuid import UUID

from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
from core.seedwork.api_layer import Router

router = Router()


class InputQueryFolderMails(BaseModel):
    group: UUID


class OutputMail(BaseModel):
    uuid: UUID


@router.get(url="folder_mails/<uuid:group>/", output_schema=list[OutputMail])
def query__folder_mails(user: OrgUser, data: InputQueryFolderMails):
    # query the mail import model from models.py
    # optional return the cc-email of the folder as well
    return []
