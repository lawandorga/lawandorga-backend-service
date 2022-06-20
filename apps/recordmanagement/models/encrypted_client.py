from django.db import models

from apps.api.models.rlc import Rlc
from apps.static.encryption import (AESEncryption, EncryptedModelMixin,
                                    RSAEncryption)


class EncryptedClient(EncryptedModelMixin, models.Model):
    from_rlc = models.ForeignKey(
        Rlc, related_name="e_client_from_rlc", on_delete=models.SET_NULL, null=True
    )
    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(null=True, blank=True)
    origin_country = models.ForeignKey(
        "OriginCountry", related_name="e_clients", on_delete=models.SET_NULL, null=True
    )
    # encrypted
    name = models.BinaryField(null=True)
    note = models.BinaryField(null=True)
    phone_number = models.BinaryField(null=True)
    encrypted_client_key = models.BinaryField(null=True)
    # encryption
    encryption_class = AESEncryption
    encrypted_fields = ["name", "note", "phone_number"]

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return "client: {};".format(self.pk)

    def encrypt(self, public_key_rlc: bytes) -> None:
        key = AESEncryption.generate_secure_key()
        self.encrypted_client_key = RSAEncryption.encrypt(key, public_key_rlc)
        super().encrypt(key)

    def decrypt(self, private_key_rlc: str = None) -> None:
        key = RSAEncryption.decrypt(self.encrypted_client_key, private_key_rlc)
        super().decrypt(key)
