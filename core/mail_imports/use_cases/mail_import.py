# import email
import logging
from email import message_from_bytes
from email.header import decode_header
from email.message import EmailMessage
from email.policy import default
from email.utils import getaddresses, parseaddr
from typing import Protocol, Sequence
from uuid import UUID

# from django.db import transaction
from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.mail_imports.mail_inbox import MailInbox, RawEmail
from core.mail_imports.models.mail_import import MailAttachement, MailImport
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


class NumEmail(Protocol):
    num: str


class EmailMessageAttachement(BaseModel):
    filename: str
    content: bytes


class ValidatedEmail(BaseModel):
    num: str
    sender: str
    to: str
    cc: str
    bcc: str
    date: str
    subject: str
    content: str
    addresses: list[str]
    # attachments: list[EmailMessageAttachement]  # TODO: this needs to get implemented


class AssignedEmail(ValidatedEmail):
    folder_uuids: list[UUID]


class FolderEmail(ValidatedEmail):
    folder_uuid: UUID
    org_pk: int


class ErrorEmail(BaseModel):
    num: str
    error: str


def get_content_from_email(message: EmailMessage):
    content = ""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True)
            if payload is not None and isinstance(payload, bytes):
                content = payload.decode()
    return content


def get_attachements_from_email(message: EmailMessage) -> list[EmailMessageAttachement]:
    attachments: list[EmailMessageAttachement] = []
    for part in message.iter_attachments():
        raise NotImplementedError("Here the EmailMessageAttachement should be created")
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
        "attachements": get_attachements_from_email(message),
    }


def validate_emails(raw_emails: list[RawEmail]) -> list[ErrorEmail | ValidatedEmail]:
    validated_emails: list[ErrorEmail | ValidatedEmail] = []
    for email in raw_emails:
        try:
            data = email.data
            message = message_from_bytes(data[0][1], policy=default)
            email_info = get_email_info(
                message
            )  # TODO: here the type does not match message_from_bytes returns a different type maybe use sth else instead of message_from_bytes?
            validated_emails.append(ValidatedEmail(num=email.num, **email_info))
        except Exception as e:
            validated_emails.append(ErrorEmail(num=email.num, error=str(e)))
    return validated_emails


def assign_email_to_folder_uuid(
    email: ValidatedEmail,
) -> AssignedEmail | ValidatedEmail:
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


def assign_emails_to_folder_uuid(
    emails: list[ValidatedEmail | ErrorEmail],
) -> list[ValidatedEmail | ErrorEmail | AssignedEmail]:
    assigned: list[ValidatedEmail | ErrorEmail | AssignedEmail] = []
    for email in emails:
        if isinstance(email, ErrorEmail):
            assigned.append(email)

        assert isinstance(email, ValidatedEmail)
        assigned.append(assign_email_to_folder_uuid(email))
    return assigned


def assign_email_to_folder(
    email: AssignedEmail, folders: dict[UUID, Folder], user: OrgUser
) -> FolderEmail | AssignedEmail:
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


def assign_emails_to_folder(
    emails: Sequence[ValidatedEmail | ErrorEmail | AssignedEmail],
    folders: dict[UUID, Folder],
    user: OrgUser,
) -> list[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail]:
    assigned: list[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail] = []
    for email in emails:
        if not isinstance(email, AssignedEmail):
            assigned.append(email)
            continue
        assigned.append(assign_email_to_folder(email, folders, user))
    return assigned


def save_emails(
    emails: Sequence[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail],
    user: OrgUser,
) -> None:
    infolder = list_filter(emails, lambda e: isinstance(e, FolderEmail))
    for email in infolder:
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
        attachements: list[MailAttachement] = []
        for attachement in email.attachements:
            attachement = MailAttachement.create(
                mail_import=obj,
            )
            attachement.upload_file(attachement.content)  # oder so
            attachements.append(attachement)
            # TODO: here the attachements need to be created from the validated_email.attachements that is not implemented yet
        obj.encrypt(user)
        with transaction.atomic():
            obj.save()
            for attachement in attachements:
                attachement.save()


def move_emails(
    mail_box: MailInbox,
    emails: Sequence[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail],
) -> None:
    infolder = list_filter(emails, lambda e: isinstance(e, FolderEmail))
    error = list_filter(emails, lambda e: isinstance(e, ErrorEmail))
    mail_box.mark_emails_as_error(error)
    mail_box.delete_emails(infolder)


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
        raw_emails = mail_box.get_raw_emails()
        validated = validate_emails(raw_emails)
        assigned = assign_emails_to_folder_uuid(validated)
        infolder = assign_emails_to_folder(assigned, folders, __actor)
        save_emails(infolder, __actor)
        move_emails(mail_box, infolder)
        log_emails(infolder)
