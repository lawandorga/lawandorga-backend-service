import uuid

from django.db import models

from core.mail.models.domain import Domain


class MailUser(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    user = models.UUIDField(unique=True)
    domain = models.ForeignKey(Domain, on_delete=models.PROTECT, db_index=True)
    pw_hash = models.CharField(max_length=1000)
    relative_path = models.CharField(max_length=100)

    class Meta:
        unique_together = ["domain", "relative_path"]
        verbose_name = "MailUser"
        verbose_name_plural = "MailUsers"

    def __str__(self):
        return "mailUser: {}; user: {};".format(self.pk, self.user)


class Alias(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    localpart = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(
        MailUser, on_delete=models.CASCADE, related_name="aliases", db_index=True
    )
    is_default = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"
        unique_together = ["user", "localpart"]

    def __str__(self):
        return "alias: {}; localpart: {};".format(self.pk, self.localpart)
