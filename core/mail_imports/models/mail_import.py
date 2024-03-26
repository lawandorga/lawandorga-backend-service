import logging
from email import message_from_bytes
from email.message import Message
from imaplib import IMAP4_SSL
from typing import Any, Sequence
from uuid import UUID, uuid4

from django.conf import settings
from django.db import models
from django.utils.timezone import localtime
from pydantic import BaseModel

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

    # org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="mail_imports")
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

    class Meta:
        verbose_name = "MI_MailImport"
        verbose_name_plural = "MI_MailImports"

    def __str__(self) -> str:
        time = localtime(self.sending_datetime).strftime("%Y-%m-%d %H:%M:%S")
        return f"mailImport: {self.folder_uuid}; time: {time};"

    def mark_as_read(self):
        self.is_read = True


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


def get_unassigned_emails(
    validated: list[ValidatedEmail], assigned: list[AssignedEmail]
) -> list[ValidatedEmail]:
    assigned_nums = [email.num for email in assigned]
    return [email for email in validated if email.num not in assigned_nums]


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


def save_emails(emails: list[AssignedEmail]):
    for email in emails:
        obj = MailImport(
            sender=email.sender,
            bcc=email.bcc or "",
            subject=email.subject,
            content=email.content,
            sending_datetime=email.date,
            folder_uuid=email.folder_uuid,
        )
        obj.save()
