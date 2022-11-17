import uuid

from django.db import models

from core.mail.models.org import MailOrg


class MailDomain(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    relative_path = models.CharField(unique=True, max_length=100)
    org = models.ForeignKey(MailOrg, related_name="domains", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"

    def __str__(self):
        return "domain: {};".format(self.pk)
