from django.db import models

from apps.api.models.user import UserProfile
from apps.static.encryption import AESEncryption, EncryptedModelMixin


class OldUserEncryptionKeys(EncryptedModelMixin, models.Model):
    user = models.OneToOneField(
        UserProfile,
        related_name="encryption_keys",
        on_delete=models.CASCADE,
        null=False,
    )
    private_key = models.BinaryField()
    private_key_encrypted = models.BooleanField(default=False)
    public_key = models.BinaryField()

    encryption_class = AESEncryption
    encrypted_fields = ["private_key"]

    class Meta:
        verbose_name = "UserEncryptionKey"
        verbose_name_plural = "UserEncryptionKeys"

    def __str__(self):
        return "userEncryptionKey: {}; user: {};".format(self.pk, self.user.email)

    def encrypt(self, password=None):
        if password is not None:
            key = password
        else:
            raise ValueError("You need to pass (password).")

        super().encrypt(key)

        if not self.private_key_encrypted:
            self.private_key_encrypted = True
            self.save()

    def decrypt(self, password=None):
        if password is not None:
            key = password
        else:
            raise ValueError("You need to pass (password).")

        if not self.private_key_encrypted:
            self.encrypt(key)
            self.private_key_encrypted = True
            self.save()

        super().decrypt(key)
