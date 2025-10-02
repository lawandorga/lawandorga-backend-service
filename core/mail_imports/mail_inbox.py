import email as _email
import logging
from imaplib import IMAP4_SSL
from typing import Any, Protocol, Sequence

from django.conf import settings
from pydantic import BaseModel

logger = logging.getLogger("django")


class UidEmail(Protocol):
    uid: str


class RawEmail(BaseModel):
    uid: str
    data: Any

    @property
    def message_id(self) -> str | None:
        """Extract the Message-ID header from the email data"""
        if self.data and len(self.data) > 0:
            raw_email = self.data[0][1]
            if isinstance(raw_email, bytes):
                msg = _email.message_from_bytes(raw_email)
                return msg.get("Message-ID")
        return None


class MailInbox:
    def __init__(self) -> None:
        self.mailbox = IMAP4_SSL(
            host=settings.MI_EMAIL_HOST, port=settings.MI_EMAIL_PORT
        )
        self.seen: set[Any] = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.mailbox.close()
            self.mailbox.logout()
        except Exception:
            pass
        if "[UNAVAILABLE]" in str(exc_val):
            logger.warning("mailbox unavailable but ignoring the error")
            return True

    def login(self):
        self.mailbox.login(settings.MI_EMAIL_USER, settings.MI_EMAIL_PASSWORD)
        self.mailbox.select("INBOX")

    def get_raw_emails(self) -> list[RawEmail]:
        _, [uids] = self.mailbox.uid("SEARCH", "", "ALL")
        emails = []
        for uid in uids.split():
            _, data = self.mailbox.uid("FETCH", uid, "(RFC822)")
            emails.append(RawEmail(uid=uid, data=data))
        return emails

    def get_raw_email(self) -> RawEmail | None:
        _, [uids] = self.mailbox.uid("SEARCH", "", "ALL")
        if not uids:
            return None
        for uid in uids.split():
            _, data = self.mailbox.uid("FETCH", uid, "(RFC822)")
            email = RawEmail(uid=uid, data=data)
            if email.message_id in self.seen:
                continue
            self.seen.add(email.message_id)
            return email
        return None

    def delete_emails(self, emails: Sequence[UidEmail]):
        for email in emails:
            try:
                self.mailbox.store(email.uid, "+FLAGS", "\\Deleted")
            except IMAP4_SSL.error as e:
                logger.warning(f"error deleting email {email.uid}: {e}")
        self.mailbox.expunge()

    def mark_emails_as_error(self, emails: Sequence[UidEmail]):
        for email in emails:
            self.mailbox.copy(email.uid, "Errors")
            self.mailbox.store(email.uid, "+FLAGS", "\\Deleted")

    def mark_emails_as_not_assignable(self, emails: Sequence[UidEmail]):
        for email in emails:
            self.mailbox.copy(email.uid, "Unassigned")
            self.mailbox.store(email.uid, "+FLAGS", "\\Deleted")

    def get_mail_attachments(self, email: UidEmail) -> list[bytes]:
        raise NotImplementedError()
