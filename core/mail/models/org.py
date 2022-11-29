from uuid import uuid4

from django.db import models


class MailOrg(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)

    class Meta:
        verbose_name = "MailOrg"
        verbose_name_plural = "MailOrgs"

    def __str__(self):
        return "mailOrg: {};".format(self.pk)
