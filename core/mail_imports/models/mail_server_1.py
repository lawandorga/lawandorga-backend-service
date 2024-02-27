from uuid import uuid4

from django.db import models

from core.mail.models.org import MailOrg


class MI_MailDomain(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    org = models.ForeignKey(
        MailOrg, related_name="domains", on_delete=models.CASCADE, null=True
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "MI_MailDomain"
        verbose_name_plural = "MI_MailDomains"


class MI_MailAddress(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    localpart = models.CharField(max_length=100, db_index=True)
    folder_uuid = models.UUIDField()
    pw_hash = models.CharField(max_length=1024)
    domain = models.ForeignKey(
        MI_MailDomain, related_name="addresses", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "MI_MailAddress"
        verbose_name_plural = "MI_MailAddress"
        ordering = ["localpart"]

    def __str__(self):
        return "address: {}; email: {}@{};".format(
            self.pk, self.localpart, self.domain.name
        )


# mail server
# abc@*.mail-import.law-orga.de
# externer mail server (?) oder eigener mail server
