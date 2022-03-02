from apps.static.encryption import EncryptedModelMixin, RSAEncryption
from apps.api.models.user import UserProfile
from apps.api.models.rlc import Rlc
from django.db import models


class UsersRlcKeys(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(UserProfile, related_name="users_rlc_keys", on_delete=models.CASCADE, null=False)
    rlc = models.ForeignKey(Rlc, related_name="encrypted_users_rlc_keys", on_delete=models.CASCADE, null=False)
    encrypted_key = models.BinaryField()

    encryption_class = RSAEncryption
    encrypted_fields = ["encrypted_key"]

    class Meta:
        verbose_name = "UserRlcKeys"
        verbose_name_plural = "UsersRlcKeys"
        unique_together = ("user", "rlc")

    def __str__(self):
        return "userRlcKeys: {}; user: {}; rlc: {};".format(self.pk, self.user.email, self.rlc.name)

    def decrypt(self, private_key_user):
        super().decrypt(private_key_user)

    def encrypt(self, public_key_user):
        super().encrypt(public_key_user)
