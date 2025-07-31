import logging
from email import message_from_bytes
from email.header import decode_header
from email.message import EmailMessage
from email.policy import default
from email.utils import getaddresses, parseaddr
from typing import Any, Protocol, Sequence
from uuid import UUID

from django.core.files.base import ContentFile
from django.db import transaction
from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.mail_imports.mail_inbox import MailInbox, RawEmail
from core.mail_imports.models.mail_import import MailAttachment, MailImport
from core.mail_imports.use_cases.finder import mail_from_uuid, mails_from_uuids
from core.seedwork.use_case_layer import use_case

from seedwork.functional import list_filter

logger = logging.getLogger("django")


@use_case
def mark_mails_as_read(__actor: OrgUser, mail_uuids: list[UUID]):
    mails = mails_from_uuids(__actor, mail_uuids)
    for mail in mails:
        mail.mark_as_read()
    MailImport.objects.bulk_update(mails, ["is_read"])


@use_case
def mark_mails_as_unread(__actor: OrgUser, mail_uuids: list[UUID]):
    mails = mails_from_uuids(__actor, mail_uuids)
    for mail in mails:
        mail.mark_as_unread()
    MailImport.objects.bulk_update(mails, ["is_read"])


@use_case
def toggle_mail_pinned(__actor: OrgUser, mail_uuid: UUID):
    mail = mail_from_uuid(__actor, mail_uuid)
    mail.toggle_pinned()
    mail.save()


class UidEmail(Protocol):
    uid: str


class EmailMessageAttachment(BaseModel):
    filename: str
    content: Any


class ValidatedEmail(BaseModel):
    uid: str
    sender: str
    to: str
    cc: str
    bcc: str
    date: str
    subject: str
    content: str
    addresses: list[str]
    attachments: list[EmailMessageAttachment] = []


class AssignedEmail(ValidatedEmail):
    folder_uuids: list[UUID]


class FolderEmail(ValidatedEmail):
    folder_uuid: UUID
    org_pk: int


class ErrorEmail(BaseModel):
    uid: str
    error: str


def get_content_from_email(message: EmailMessage):
    content = ""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True)
            if payload is not None and isinstance(payload, bytes):
                charset = part.get_content_charset() or "utf-8"
                content = payload.decode(charset, errors="replace")
    return content


def get_attachments_from_email(message: EmailMessage) -> list[EmailMessageAttachment]:
    attachments: list[EmailMessageAttachment] = []
    for part in message.iter_attachments():
        attachment = EmailMessageAttachment(
            filename=part.get_filename() or "Unknown",
            content=part.get_payload(decode=True),
        )
        attachments.append(attachment)
    return attachments


def get_sender_info(message: EmailMessage) -> str:
    sender = message.get("From")
    if sender is None:
        return "unknown"

    name, email = parseaddr(sender)

    decoded_name = decode_header(name)[0][0]
    if isinstance(decoded_name, bytes):
        name = decoded_name.decode()

    return f"{name} <{email}>"


def get_to_info(message: EmailMessage) -> str:
    raw_to = message.get("To", "")
    if raw_to is None:
        return ""

    addresses = getaddresses([raw_to])
    formatted_addresses = []
    for name, email in addresses:
        decoded_name = decode_header(name)[0][0]
        if isinstance(decoded_name, bytes):
            name = decoded_name.decode()
        formatted_addresses.append(f"{name} <{email}>")

    return ", ".join(formatted_addresses)


def get_addresses_from_message(message: EmailMessage) -> list[str]:
    addresses_and_name = []
    for header in ["To", "CC", "BCC"]:
        raw_header = message.get(header, "")
        if raw_header is None:
            continue

        addresses_and_name.extend(getaddresses([raw_header]))

    addresses = [email for _, email in addresses_and_name]

    return addresses


def get_email_info(message: EmailMessage):
    return {
        "sender": get_sender_info(message),
        "to": get_to_info(message),
        "bcc": message.get("BCC", ""),
        "cc": message.get("CC", ""),
        "date": message.get("Date"),
        "subject": message.get("Subject"),
        "content": get_content_from_email(message),
        "addresses": get_addresses_from_message(message),
        "attachments": get_attachments_from_email(message),
    }


def validate_email(raw_email: RawEmail) -> ErrorEmail | ValidatedEmail:
    try:
        data = raw_email.data
        message: EmailMessage = message_from_bytes(
            data[0][1], policy=default  # type: ignore
        )
        email_info = get_email_info(message)
        return ValidatedEmail(uid=raw_email.uid, **email_info)
    except Exception as e:
        logger.error(f"error while importing mail: {e}")
        return ErrorEmail(uid=raw_email.uid, error=str(e))


def assign_email_to_folder_uuid(
    email: ValidatedEmail | ErrorEmail,
) -> AssignedEmail | ValidatedEmail | ErrorEmail:
    if isinstance(email, ErrorEmail):
        return email
    folder_uuids = []
    for address in email.addresses:
        left = address.split("@")[0]
        try:
            folder_uuid = UUID(left)
            folder_uuids.append(folder_uuid)
        except Exception:
            continue
    if folder_uuids:
        return AssignedEmail(folder_uuids=folder_uuids, **email.model_dump())
    return email


def assign_email_to_folder(
    email: AssignedEmail | ValidatedEmail | ErrorEmail,
    folders: dict[UUID, Folder],
    user: OrgUser,
) -> FolderEmail | AssignedEmail | ValidatedEmail | ErrorEmail:
    if not isinstance(email, AssignedEmail):
        return email
    for folder_uuid in email.folder_uuids:
        if folder_uuid not in folders:
            continue
        folder = folders[folder_uuid]
        assert folder.org_pk is not None
        if not folder.has_access(user):
            continue
        return FolderEmail(
            org_pk=folder.org_pk, **email.model_dump(), folder_uuid=folder_uuid
        )
    return email


def save_email(
    email: ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail,
    user: OrgUser,
) -> None:
    if not isinstance(email, FolderEmail):
        return
    assert isinstance(email, FolderEmail)
    obj = MailImport.create(
        sender=email.sender,
        bcc=email.bcc or "",
        to=email.to,
        subject=email.subject,
        content=email.content,
        sending_datetime=email.date,
        folder_uuid=email.folder_uuid,
        org_id=email.org_pk,
    )
    obj.encrypt(user)
    attachments: list[MailAttachment] = []
    for a in email.attachments:
        if a.content is None or len(a.content) == 0:
            continue
        content_file = ContentFile(content=a.content, name=a.filename)
        attachment = MailAttachment.create(
            mail_import=obj,
            filename=a.filename,
            content=content_file,
            user=user,
        )
        attachments.append(attachment)
    with transaction.atomic():
        obj.save()
        for attachment in attachments:
            attachment.save()


def move_email(
    mail_box: MailInbox,
    email: ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail,
) -> None:
    if isinstance(email, FolderEmail):
        mail_box.delete_emails([email])
    elif isinstance(email, ErrorEmail):
        mail_box.mark_emails_as_error([email])


def log_emails(
    emails: Sequence[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail],
):
    validated = list_filter(emails, lambda e: type(e) is ValidatedEmail)
    error = list_filter(emails, lambda e: type(e) is ErrorEmail)
    assigned = list_filter(emails, lambda e: type(e) is AssignedEmail)
    infolder = list_filter(emails, lambda e: type(e) is FolderEmail)
    logger.info(f"total: {len(emails)}")
    logger.info(f"validated: {len(validated)}")
    logger.info(f"error: {len(error)}")
    logger.info(f"assigned: {len(assigned)}")
    logger.info(f"infolder: {len(infolder)}")


@use_case
def import_mails(__actor: OrgUser, r: FolderRepository):
    folders = r.get_dict(__actor.org_id)
    with MailInbox() as mail_box:
        mail_box.login()
        all_mails = []
        while email := mail_box.get_raw_email():
            validated = validate_email(email)
            assigned = assign_email_to_folder_uuid(validated)
            infolder = assign_email_to_folder(assigned, folders, __actor)
            save_email(infolder, __actor)
            move_email(mail_box, infolder)
            all_mails.append(infolder)
        log_emails(all_mails)
