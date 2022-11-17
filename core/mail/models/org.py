import uuid

from django.db import models


class MailOrg(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)

    class Meta:
        verbose_name = "MailOrg"
        verbose_name_plural = "MailOrgs"

    def __str__(self):
        return "mailOrg: {};".format(self.pk)
