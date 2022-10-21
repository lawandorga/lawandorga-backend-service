from django.db import models

from core.auth.models import UserProfile
from core.rlc.models import Org
from core.seedwork.encryption import EncryptedModelMixin, RSAEncryption


class OrgEncryption(EncryptedModelMixin, models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="users_rlc_keys", on_delete=models.CASCADE, null=False
    )
    rlc = models.ForeignKey(
        Org,
        related_name="encrypted_users_rlc_keys",
        on_delete=models.CASCADE,
        null=False,
    )
    encrypted_key = models.BinaryField()
    correct = models.BooleanField(default=True)

    encryption_class = RSAEncryption
    encrypted_fields = ["encrypted_key"]

    class Meta:
        verbose_name = "UserRlcKeys"
        verbose_name_plural = "UsersRlcKeys"
        unique_together = ("user", "rlc")

    def __str__(self):
        return "userRlcKeys: {}; user: {}; rlc: {};".format(
            self.pk, self.user.email, self.rlc.name
        )

    def set_correct(self, value):
        key = OrgEncryption.objects.get(pk=self.pk)
        key.correct = value
        key.save()
        self.correct = value

    def test(self, private_key_user):
        try:
            super().decrypt(private_key_user)
            self.set_correct(True)
        except ValueError:
            self.set_correct(False)
            self.user.rlc_user.locked = True
            self.user.rlc_user.save(update_fields=["locked"])

    def decrypt(self, private_key_user):
        try:
            super().decrypt(private_key_user)
        except Exception as e:
            self.test(private_key_user)
            raise e

    def encrypt(self, public_key_user):
        super().encrypt(public_key_user)
