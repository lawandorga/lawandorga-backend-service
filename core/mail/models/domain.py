from uuid import uuid4

from django.db import models

from core.mail.models.org import MailOrg


class MailDomain(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    org = models.ForeignKey(
        MailOrg, related_name="domains", on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = "MailDomain"
        verbose_name_plural = "MailDomains"

    def __str__(self):
        return "mailDomain: {};".format(self.pk)
