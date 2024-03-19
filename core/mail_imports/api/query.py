import datetime
from uuid import UUID

from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
<<<<<<< HEAD
from core.mail_imports.models import MailImport
=======
from core.mail_imports.models.mail_import import MailImport
>>>>>>> 1b75d6306047666fbcf1f4dedcd499d6b9c022a0
from core.seedwork.api_layer import Router

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


@router.get(url="folder_mails/get_cc_address", output_schema=str)
def query__get_cc_address(user: OrgUser):
    return user.email


@router.get(url="folder_mails/<uuid:group>/", output_schema=list[OutputMail])
def query__folder_mails(data: InputQueryFolderMails):
    imported_mails = MailImport.objects.filter(folder_uuid=data.group)
    mails = []
    for imported_mail in imported_mails:
        mail = OutputMail(
            uuid=imported_mail.uuid,
            sender=imported_mail.sender,
            bcc=imported_mail.bcc,
            subject=imported_mail.subject,
            content=imported_mail.content,
            sending_datetime=imported_mail.sending_datetime,
            is_read=imported_mail.is_read,
            is_pinned=imported_mail.is_pinned,
        )
        mails.append(mail)
    return mails
