import logging
from imaplib import IMAP4_SSL
from typing import Any, Protocol, Sequence

from django.conf import settings
from pydantic import BaseModel

logger = logging.getLogger("django")


class NumEmail(Protocol):
    num: str


class RawEmail(BaseModel):
    num: str
    data: Any


class MailInbox:
    def __init__(self) -> None:
        self.mailbox = IMAP4_SSL(
            host=settings.MI_EMAIL_HOST, port=settings.MI_EMAIL_PORT
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.mailbox.close()
            self.mailbox.logout()
        except Exception:
            pass
        if "[UNAVAILABLE]" in str(exc_val):
            logger.error("mailbox unavailable but ignoring the error")
            return True

    def login(self):
        self.mailbox.login(settings.MI_EMAIL_USER, settings.MI_EMAIL_PASSWORD)
        self.mailbox.select("INBOX")

    def get_raw_emails(self) -> list[RawEmail]:
        _, [nums] = self.mailbox.search(None, "ALL")
        emails = []
        for num in nums.split():
            _, data = self.mailbox.fetch(num, "(RFC822)")
            emails.append(RawEmail(num=num, data=data))
        return emails

    def delete_emails(self, emails: Sequence[NumEmail]):
        for email in emails:
            self.mailbox.copy(email.num, "Trash")
            self.mailbox.store(email.num, "+FLAGS", "\\Deleted")

    def mark_emails_as_error(self, emails: Sequence[NumEmail]):
        for email in emails:
            self.mailbox.copy(email.num, "Errors")
            self.mailbox.store(email.num, "+FLAGS", "\\Deleted")

    def mark_emails_as_not_assignable(self, emails: Sequence[NumEmail]):
        for email in emails:
            self.mailbox.copy(email.num, "Unassigned")
            self.mailbox.store(email.num, "+FLAGS", "\\Deleted")

    def get_mail_attachments(self, email: NumEmail) -> list[bytes]:
        raise NotImplementedError()
