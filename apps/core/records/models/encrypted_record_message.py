from typing import Optional

from django.db import models

from apps.core.auth.models import RlcUser
from apps.core.records.models.record import Record
from apps.static.encryption import AESEncryption, EncryptedModelMixin


class EncryptedRecordMessage(EncryptedModelMixin, models.Model):
    sender = models.ForeignKey(
        RlcUser,
        related_name="messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    record = models.ForeignKey(
        Record, related_name="messages", on_delete=models.CASCADE, null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # encrypted
    message = models.BinaryField(null=False)

    encryption_class = AESEncryption
    encrypted_fields = ["message"]

    class Meta:
        ordering = ["created"]
        verbose_name = "RecordMessage"
        verbose_name_plural = "RecordMessages"

    def __str__(self):
        return "recordMessage: {}; record: {};".format(self.pk, self.record.pk)

    def encrypt(self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None):
        if user and private_key_user:
            record_encryption = self.record.encryptions.get(user=user)
            record_encryption.decrypt(private_key_user)
            key = record_encryption.key
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (user and private_key_user) or (aes_key_record)."
            )
        super().encrypt(key)

    def decrypt(self, user: Optional[RlcUser] = None, private_key_user=None, aes_key_record=None):
        if user and private_key_user:
            record_encryption = self.record.encryptions.get(user=user)
            record_encryption.decrypt(private_key_user)
            key = record_encryption.key
        elif aes_key_record:
            key = aes_key_record
        else:
            raise ValueError(
                "You have to set (user and private_key_user) or (aes_key)."
            )
        super().decrypt(key)
