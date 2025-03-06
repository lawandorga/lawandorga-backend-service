from uuid import uuid4

from django.db import models

from core.mail.models.user import MailUser


class MailAdmin(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    user = models.OneToOneField(
        MailUser, related_name="admin", on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "MAIL_MailAdmin"
        verbose_name_plural = "MAIL_MailAdmins"

    def __str__(self):
        return "mailAdmin: {};".format(self.pk)
