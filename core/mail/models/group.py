from uuid import uuid4

from django.db import models

from core.mail.models.org import MailOrg
from core.mail.models.user import MailUser


class MailGroup(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    org = models.ForeignKey(MailOrg, related_name="groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(MailUser, related_name="groups")

    class Meta:
        verbose_name = "MailGroup"
        verbose_name_plural = "MailGroups"

    def __str__(self):
        return "mailGroup: {};".format(self.id)

    @property
    def email(self):
        address = self.account.addresses.filter(is_default=True).first()
        if address is None:
            return None
        return address.address
