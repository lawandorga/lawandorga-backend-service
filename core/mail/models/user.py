import uuid

from django.db import models

from core.auth.models import UserProfile
from core.mail.models import MailDomain
from core.mail.models.org import MailOrg


class MailUser(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        UserProfile, related_name="mail_user", on_delete=models.CASCADE
    )
    pw_hash = models.CharField(max_length=1000)
    relative_path = models.CharField(max_length=100)
    org = models.ForeignKey(MailOrg, related_name="members", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "MailUser"
        verbose_name_plural = "MailUsers"

    def __str__(self):
        return "mailUser: {}; user: {};".format(self.pk, self.user)


class MailAlias(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    localpart = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(
        MailUser, on_delete=models.CASCADE, related_name="aliases", db_index=True
    )
    is_default = models.BooleanField(default=False, db_index=True)
    domain = models.ForeignKey(
        MailDomain, related_name="aliases", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"
        unique_together = ["user", "localpart"]

    def __str__(self):
        return "alias: {}; localpart: {};".format(self.pk, self.localpart)
