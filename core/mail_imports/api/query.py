import datetime
from uuid import UUID

from django.http import FileResponse
from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import OrgUser
from core.mail_imports.models.mail_import import MailAttachment, MailImport
from core.seedwork.api_layer import Router

router = Router()


class InputQueryFolderMails(BaseModel):
    folder_uuid: UUID


class OutputMailAttachment(BaseModel):
    name: str
    uuid: UUID


class OutputMail(BaseModel):
    uuid: UUID
    sender: str
    to: str
    bcc: str
    subject: str
    content: str
    sending_datetime: datetime.datetime
    is_read: bool
    is_pinned: bool
    mail_attachments: list[OutputMailAttachment]

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


@router.get(url="folder_mails/get_cc_address", output_schema=str)
def query__get_cc_address(user: OrgUser):
    return user.email


@router.get(url="folder_mails/<uuid:folder_uuid>/", output_schema=list[OutputMail])
def query__folder_mails(user: OrgUser, data: InputQueryFolderMails):
    mails = list(
        MailImport.objects.prefetch_related("attachments").filter(
            folder_uuid=data.folder_uuid
        )
    )
    output_mails = []
    for mail in mails:
        mail.decrypt(user)
        output_mails.append(
            OutputMail(
                uuid=mail.uuid,
                to=mail.to,
                bcc=mail.bcc,
                subject=mail.subject,
                content=mail.content,
                is_pinned=mail.is_pinned,
                is_read=mail.is_read,
                sender=mail.sender,
                sending_datetime=mail.sending_datetime,
                mail_attachments=[
                    OutputMailAttachment(name=attachment.filename, uuid=attachment.uuid)
                    for attachment in list(mail.attachments.all())
                ],
            )
        )
    return output_mails


class InputAttachementId(BaseModel):
    uuid: UUID


@router.get("mail_attachments/<uuid:uuid>/", output_schema=FileResponse)
def query__mail_attachement(user: OrgUser, data: InputAttachementId):
    attachement = MailAttachment.objects.filter(mail_import__org_id=user.org_id).get(
        uuid=data.uuid
    )
    file = attachement.get_decrypted_file(user)
    return FileResponse(file, filename=attachement.filename, as_attachment=True)
