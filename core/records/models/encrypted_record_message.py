from django.db import models

from core.auth.models import RlcUser
from core.records.models.record import Record
from core.seedwork.encryption import AESEncryption, EncryptedModelMixin


class EncryptedRecordMessage(EncryptedModelMixin, models.Model):
    sender = models.ForeignKey(
        RlcUser,
        related_name="messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    record = models.ForeignKey(
        Record, related_name="messages", on_delete=models.CASCADE
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

    def encrypt(self, user: RlcUser, private_key_user=None, aes_key_record=None):
        key = self.record.get_aes_key(user)
        super().encrypt(key)

    def decrypt(self, user: RlcUser, private_key_user=None, aes_key_record=None):
        key = self.record.get_aes_key(user)
        super().decrypt(key)
