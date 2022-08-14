from django.db import models

from apps.core.models import UserProfile
from apps.recordmanagement.models import EncryptedRecord  # type: ignore
from apps.static.encryption import EncryptedModelMixin, RSAEncryption


class RecordEncryption(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="record_encryptions", on_delete=models.CASCADE
    )
    record = models.ForeignKey(
        EncryptedRecord, related_name="encryptions", on_delete=models.CASCADE
    )
    encrypted_key = models.BinaryField()

    encryption_class = RSAEncryption
    encrypted_fields = ["encrypted_key"]

    class Meta:
        unique_together = ("user", "record")
        verbose_name = "RecordEncryption"
        verbose_name_plural = "RecordEncryptions"

    def __str__(self):
        return "recordEncryption: {}; user: {}; record: {};".format(
            self.id, self.user.email, self.record.record_token
        )

    def encrypt(self, public_key_user=None):
        if public_key_user:
            key = public_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        super().encrypt(key)

    def decrypt(self, private_key_user=None):
        if private_key_user:
            key = private_key_user
        else:
            raise ValueError("You need to pass (private_key_user).")
        super().decrypt(key)
