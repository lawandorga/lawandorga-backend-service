from apps.static.encryption import AESEncryption, EncryptedModelMixin
from apps.api.models.rlc import Rlc
from django.db import models


class RlcEncryptionKeys(EncryptedModelMixin, models.Model):
    rlc = models.OneToOneField(
        Rlc, related_name="encryption_keys", on_delete=models.CASCADE
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

    def decrypt(self, aes_key: str) -> None:
        super().decrypt(aes_key)

    def encrypt(self, aes_key: str) -> None:
        super().encrypt(aes_key)