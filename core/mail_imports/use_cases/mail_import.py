import logging
from email import message_from_bytes
from email.message import Message
from typing import Protocol, Sequence
from uuid import UUID

from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.repositories.folder import FolderRepository
from core.mail_imports.mail_inbox import MailInbox, RawEmail
from core.mail_imports.models.mail_import import MailImport
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
def toggle_mail_pinned(__actor: OrgUser, mail_uuid: UUID):
    mail = mail_from_uuid(__actor, mail_uuid)
    mail.toggle_pinned()
    mail.save()
    # MailImport.objects.update()


class NumEmail(Protocol):
    num: str


class ValidatedEmail(BaseModel):
    num: str
    sender: str
    to: str
    cc: str
    bcc: str
    date: str
    subject: str
    content: str

    @property
    def email_addresses(self) -> list[str]:
        e1 = self.to.split(",")
        e2 = self.bcc.split(",")
        e3 = self.cc.split(",")
        e4 = e1 + e2 + e3
        e5 = [e.strip() for e in e4]
        return e5


class AssignedEmail(ValidatedEmail):
    folder_uuids: list[UUID]


class FolderEmail(ValidatedEmail):
    folder_uuid: UUID
    org_pk: int


class ErrorEmail(BaseModel):
    num: str
    error: str


def get_content_from_email(message: Message):
    content = ""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            content += str(part)
    return content


def get_email_info(message: Message):
    return {
        "sender": message.get("From"),
        "to": message.get("To"),
        "bcc": message.get("BCC", ""),
        "cc": message.get("CC", ""),
        "date": message.get("Date"),
        "subject": message.get("Subject"),
        "content": get_content_from_email(message),
    }


def validate_emails(raw_emails: list[RawEmail]) -> list[ErrorEmail | ValidatedEmail]:
    validated_emails: list[ErrorEmail | ValidatedEmail] = []
    for email in raw_emails:
        try:
            data = email.data
            message = message_from_bytes(data[0][1])
            email_ = get_email_info(message)
            validated_emails.append(ValidatedEmail(num=email.num, **email_))
        except Exception as e:
            validated_emails.append(ErrorEmail(num=email.num, error=str(e)))
    return validated_emails


def assign_email_to_folder_uuid(
    email: ValidatedEmail,
) -> AssignedEmail | ValidatedEmail:
    folder_uuids = []
    for address in email.email_addresses:
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
    email: AssignedEmail, folders: dict[UUID, Folder]
) -> FolderEmail | AssignedEmail:
    for folder_uuid in email.folder_uuids:
        if folder_uuid not in folders:
            continue
        folder = folders[folder_uuid]
        assert folder.org_pk is not None
        return FolderEmail(
            org_pk=folder.org_pk, **email.model_dump(), folder_uuid=folder_uuid
        )
    return email


def assign_emails_to_folder(
    emails: Sequence[ValidatedEmail | ErrorEmail | AssignedEmail],
    folders: dict[UUID, Folder],
) -> list[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail]:
    assigned: list[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail] = []
    for email in emails:
        if not isinstance(email, AssignedEmail):
            assigned.append(email)
            continue
        assigned.append(assign_email_to_folder(email, folders))
    return assigned


def save_emails(
    emails: Sequence[ValidatedEmail | ErrorEmail | AssignedEmail | FolderEmail],
) -> None:
    infolder = list_filter(emails, lambda e: isinstance(e, FolderEmail))
    for email in infolder:
        assert isinstance(email, FolderEmail)
        obj = MailImport(
            sender=email.sender,
            bcc=email.bcc or "",
            subject=email.subject,
            content=email.content,
            sending_datetime=email.date,
            folder_uuid=email.folder_uuid,
            org_id=email.org_pk,
        )
        obj.save()


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
        infolder = assign_emails_to_folder(assigned, folders)
        save_emails(infolder)
        move_emails(mail_box, infolder)
        log_emails(infolder)
