"""
This file contains the model for the mail import.
"""

import email
from imaplib import IMAP4_SSL
from uuid import uuid4

from django.conf import settings
from django.db import models


class MailImport(models.Model):
    """
    This is the db model for mail import.
    """

    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    sender = models.CharField(max_length=255, blank=False)
    bcc = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(max_length=255, blank=True)
    sending_datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


def get_emails_from_server():
    """
    Fetch mails from mailbox via IMAP
    """
    mailbox = IMAP4_SSL(host=settings.MI_EMAIL_HOST, port=settings.MI_EMAIL_PORT)
    mailbox.login(settings.MI_EMAIL_USER, settings.MI_EMAIL_PASSWORD)
    mailbox.select("Inbox")
    _, data = mailbox.search(None, "UNSEEN")
    emails = []
    for num in data[0].split():
        _, data = mailbox.fetch(num, "(RFC822)")
        message = email.message_from_bytes(data[0][1])
        email_ = get_email_info(message)
        emails.append(email_)
    mailbox.close()
    mailbox.logout()
    return emails


def get_email_info(message):
    return {
        "from": message.get("From"),
        "to": message.get("To"),
        "BCC": message.get("BCC"),
        "date": message.get("Date"),
        "subject": message.get("Subject"),
        "content": get_content_from_email(message),
    }


def get_content_from_email(message):
    content = ""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            content += part
    return content


def save_emails():
    emails = get_emails_from_server()
    for email_ in emails:
        obj = MailImport(
            sender=email_["from"],
            bcc=email_["BCC"],
            subject=email_["subject"],
            content=email_["content"],
            date=email_["sending_datetime"],
        )
        obj.save()
