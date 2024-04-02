import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import OrgUser
from core.mail_imports.models.mail_import import MailImport
from core.seedwork.api_layer import Router

from seedwork.functional import list_map

router = Router()


class InputQueryFolderMails(BaseModel):
    folder_uuid: UUID


class OutputMail(BaseModel):
    uuid: UUID
    sender: str
    bcc: str
    subject: str
    content: str
    sending_datetime: datetime.datetime
    is_read: bool
    is_pinned: bool

    model_config = ConfigDict(from_attributes=True)


@router.get(url="folder_mails/get_cc_address", output_schema=str)
def query__get_cc_address(user: OrgUser):
    return user.email


@router.get(url="folder_mails/<uuid:folder_uuid>/", output_schema=list[OutputMail])
def query__folder_mails(user: OrgUser, data: InputQueryFolderMails):
    mails = list(MailImport.objects.filter(folder_uuid=data.folder_uuid))
    mails = list_map(mails, lambda m: m.decrypt(user))
    return mails
