from uuid import uuid4

from django.db import models

from core.mail.models import MailAccount
from core.mail.models.domain import MailDomain


class MailAddress(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    localpart = models.CharField(max_length=100, db_index=True)
    account = models.ForeignKey(
        MailAccount, on_delete=models.CASCADE, related_name="addresses", db_index=True
    )
    is_default = models.BooleanField(default=False, db_index=True)
    domain = models.ForeignKey(
        MailDomain, related_name="addresses", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"

    def __str__(self):
        return "address: {}; email: {}@{};".format(
            self.pk, self.localpart, self.domain.name
        )

    @property
    def address(self):
        return "{}@{}".format(self.localpart, self.domain.name)
