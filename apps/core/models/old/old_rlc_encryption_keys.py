from django.db import models

from apps.core.models.rlc import Org
from apps.static.encryption import AESEncryption, EncryptedModelMixin


class OldRlcEncryptionKeys(EncryptedModelMixin, models.Model):
    rlc = models.OneToOneField(
        Org, related_name="encryption_keys", on_delete=models.CASCADE
    )
    public_key = models.BinaryField()
    encrypted_private_key = models.BinaryField()

    encrypted_fields = ["encrypted_private_key"]
    encryption_class = AESEncryption

    class Meta:
        verbose_name = "RlcEncryptionKey"
        verbose_name_plural = "RlcEncryptionKeys"

    def __str__(self):
        return "rlcEncryptionKey: {}; rlc: {};".format(self.pk, self.rlc.name)

    def decrypt(self, aes_key):
        super().decrypt(aes_key)

    def encrypt(self, aes_key):
        super().encrypt(aes_key)
