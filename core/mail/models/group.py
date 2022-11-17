import uuid

from django.db import models

from core.mail.models.org import MailOrg
from core.mail.models.user import MailUser


class MailGroup(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    org = models.ForeignKey(MailOrg, related_name="groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(MailUser, related_name="groups")

    class Meta:
        verbose_name = "MailGroup"
        verbose_name_plural = "MailGroups"

    def __str__(self):
        return "mailGroup: {};".format(self.id)
