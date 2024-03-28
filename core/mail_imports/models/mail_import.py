import logging
from email import message_from_bytes
from email.message import Message
from imaplib import IMAP4_SSL
from typing import TYPE_CHECKING, Any, Protocol, Sequence, TypeVar
from uuid import UUID, uuid4

from django.conf import settings
from django.db import models
from django.utils.timezone import localtime
from pydantic import BaseModel

from core.auth.models.org_user import OrgUser
from core.folders.domain.aggregates.folder import Folder

# from core.folders.domain.value_objects.box import OpenBox
from core.folders.domain.value_objects.symmetric_key import (
    EncryptedSymmetricKey,
    SymmetricKey,
)
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.folders.infrastructure.symmetric_encryptions import SymmetricEncryptionV1
from core.rlc.models.org import Org

logger = logging.getLogger("django")


class MailImport(models.Model):
    @classmethod
    def create(cls, sender: str, subject: str, content: str, folder_uuid: UUID):
        return cls(
            sender=sender,
            subject=subject,
            content=content,
            folder_uuid=folder_uuid,
        )

    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="mail_imports")
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True, editable=False)
    sender = models.CharField(max_length=255, blank=False)
    cc = models.CharField(max_length=255, blank=True)
    bcc = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(max_length=255, blank=True)
    sending_datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    folder_uuid = models.UUIDField(db_index=True)

    if TYPE_CHECKING:
        org_id: int

    class Meta:
        verbose_name = "MI_MailImport"
        verbose_name_plural = "MI_MailImports"

    @property
    def folder(self) -> Folder:
        assert self.folder_uuid is not None
        if not hasattr(self, "_folder"):
            r = DjangoFolderRepository()
            self._folder = r.retrieve(self.org_id, self.folder_uuid)
        return self._folder

    def __str__(self) -> str:
        time = localtime(self.sending_datetime).strftime("%Y-%m-%d %H:%M:%S")
        return f"mailImport: {self.folder_uuid}; time: {time};"

    def mark_as_read(self):
        self.is_read = True

    def encrypt(self, user: OrgUser):
        raise NotImplementedError("where to get the asymmetric key?")
        # assert self.folder_uuid is not None

        # self.__generate_key(user)
        # key = self.get_key(user)
        # open_box = OpenBox(data=self.content.encode("utf-8"))
        # locked_box = key.lock(open_box)
        # self.enc_content = locked_box.as_dict()

    def decrypt(self):
        raise NotImplementedError()

    def __generate_key(self, user: OrgUser):
        assert self.folder is not None

        key = SymmetricKey.generate(SymmetricEncryptionV1)
        lock_key = self.folder.get_encryption_key(requestor=user)
        enc_key = EncryptedSymmetricKey.create(key, lock_key)
        self.key = enc_key.as_dict()

    def get_key(self, user: OrgUser) -> SymmetricKey:
        assert self.folder is not None

        enc_key = EncryptedSymmetricKey.create_from_dict(self.key)
        unlock_key = self.folder.get_decryption_key(requestor=user)
        key = enc_key.decrypt(unlock_key)
        return key


class NumEmail(Protocol):
    num: str


class RawEmail(BaseModel):
    num: str
    data: Any


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
    folder_uuid: UUID


class FolderEmail(AssignedEmail):
    org_pk: int


class ErrorEmail(BaseModel):
    num: str
    error: str


class MailInbox:
    def __init__(self) -> None:
        self.mailbox = IMAP4_SSL(
            host=settings.MI_EMAIL_HOST, port=settings.MI_EMAIL_PORT
        )

    def __enter__(self):
        self.mailbox.login(settings.MI_EMAIL_USER, settings.MI_EMAIL_PASSWORD)
        self.mailbox.select("INBOX")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mailbox.close()
        self.mailbox.logout()

    def get_raw_emails(self):
        _, [nums] = self.mailbox.search(None, "ALL")
        emails = []
        for num in nums.split():
            _, data = self.mailbox.fetch(num, "(RFC822)")
            emails.append(RawEmail(num=num, data=data))
        return emails

    def delete_emails(self, emails: Sequence[ValidatedEmail | ErrorEmail | RawEmail]):
        for email in emails:
            self.mailbox.copy(email.num, "Trash")
            self.mailbox.store(email.num, "+FLAGS", "\\Deleted")

    def mark_emails_as_error(self, emails: list[ErrorEmail]):
        for email in emails:
            logger.warning(f"Error in email {email.num}: {email.error}")
            self.mailbox.copy(email.num, "Errors")
            self.mailbox.store(email.num, "+FLAGS", "\\Deleted")

    def mark_emails_as_not_assignable(
        self, emails: Sequence[ValidatedEmail | ErrorEmail | RawEmail]
    ):
        for email in emails:
            self.mailbox.copy(email.num, "Unassigned")
            self.mailbox.store(email.num, "+FLAGS", "\\Deleted")


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


def assign_emails(emails: list[ValidatedEmail]) -> list[AssignedEmail]:
    assigned_emails: list[AssignedEmail] = []
    for email in emails:
        for address in email.email_addresses:
            left = address.split("@")[0]
            try:
                folder_uuid = UUID(left)
                assigned_emails.append(
                    AssignedEmail(folder_uuid=folder_uuid, **email.model_dump())
                )
            except Exception:
                continue
    return assigned_emails


def put_emails_in_folders(
    emails: list[AssignedEmail], folders: dict[UUID, int]
) -> list[FolderEmail]:
    folder_emails: list[FolderEmail] = []
    for email in emails:
        org_pk = folders.get(email.folder_uuid)
        if org_pk:
            folder_emails.append(FolderEmail(org_pk=org_pk, **email.model_dump()))
    return folder_emails


E1 = TypeVar("E1", bound=NumEmail)
E2 = TypeVar("E2", bound=NumEmail)


def get_subset_of_emails(all_emails: list[E1], to_exclude: list[E2]) -> list[E1]:
    assigned_nums = [email.num for email in to_exclude]
    return [email for email in all_emails if email.num not in assigned_nums]


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


def get_content_from_email(message: Message):
    content = ""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            content += str(part)
    return content


def save_emails(emails: list[FolderEmail]):
    for email in emails:
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
