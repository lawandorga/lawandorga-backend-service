from uuid import uuid4

from django.db import models
from django.db.models import Q

from core.mail.models.group import MailGroup
from core.mail.models.user import MailUser


class MailAccount(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid4, unique=True)
    relative_path = models.UUIDField(unique=True, default=uuid4)
    group = models.OneToOneField(
        MailGroup, related_name="account", on_delete=models.CASCADE, null=True
    )
    user = models.OneToOneField(
        MailUser, related_name="account", on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name = "MailAccount"
        verbose_name_plural = "MailAccounts"
        constraints = [
            models.CheckConstraint(
                check=(Q(group__isnull=True) & Q(user__isnull=False))
                | (Q(group__isnull=False) & Q(user__isnull=True)),
                name="one_of_both_is_set",
            )
        ]

    def __str__(self):
        return "mailAccount: {};".format(self.id)
