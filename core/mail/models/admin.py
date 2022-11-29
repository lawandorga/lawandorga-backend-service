from uuid import uuid4

from django.db import models

from core.mail.models.user import MailUser


class MailAdmin(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4)
    user = models.OneToOneField(
        MailUser, related_name="admin", on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "MailAdmin"
        verbose_name_plural = "MailAdmins"

    def __str__(self):
        return "mailAdmin: {};".format(self.id)
