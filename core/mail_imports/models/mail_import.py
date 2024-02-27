"""
This file contains the model for the mail import.
"""

from uuid import uuid4

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
