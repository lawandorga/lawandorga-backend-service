import re
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
        verbose_name = "MailAddress"
        verbose_name_plural = "MailAddress"

    def __str__(self):
        return "address: {}; email: {}@{};".format(
            self.pk, self.localpart, self.domain.name
        )

    @property
    def address(self):
        return "{}@{}".format(self.localpart, self.domain.name)

    @staticmethod
    def check_localpart(localpart: str):
        if not isinstance(localpart, str):
            raise TypeError(
                "The type should be 'str' not '{}'.".format(type(localpart))
            )
        if len(localpart) > 64:
            raise ValueError("The localpart is too long.")
        count = localpart.count(".")
        if count > 1:
            raise ValueError(
                "The localpart contains '.' {} times. '.' is only allowed once.".format(
                    count
                )
            )
        if len(localpart) <= 1:
            raise ValueError("The localpart is too short.")
        regex = r"^([a-z]|[0-9]|\.|-|_)+$"
        pattern = re.compile(regex)
        if not pattern.match(localpart):
            raise ValueError(
                "You are only allowed to use the following characters [a-z], [0-9], ., - or _."
            )
        regex = r"^([a-z]|[0-9]).+([a-z]|[0-9])$"
        pattern = re.compile(regex)
        if not pattern.match(localpart):
            raise ValueError(
                "The localpart needs to start and end with [a-z] or [0-9]."
            )
