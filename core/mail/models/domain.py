import re
from uuid import uuid4

from django.db import models

from core.mail.models.org import MailOrg


class MailDomain(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    org = models.ForeignKey(
        MailOrg, related_name="domains", on_delete=models.CASCADE, null=True
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "MailDomain"
        verbose_name_plural = "MailDomains"

    def __str__(self):
        return "mailDomain: {};".format(self.pk)

    @staticmethod
    def check_domain(domain: str):
        if not isinstance(domain, str):
            raise TypeError(
                "The domain should be of type 'str' but is '{}'.".format(type(domain))
            )

        if len(domain) < 1:
            raise ValueError('The domain is too short.')

        if len(domain) > 64:
            raise ValueError('The domain is too long.')

        regex = "^((?!-)[a-z0-9-]+(?<!-)\\.)+(?!-)[a-z-]{2,20}(?<!-)$"
        pattern = re.compile(regex)
        if not pattern.match(domain):
            raise ValueError(
                "The domain contains illegal characters or does not conform to the correct structure."
            )
