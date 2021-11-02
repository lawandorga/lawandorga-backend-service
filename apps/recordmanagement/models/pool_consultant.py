from apps.api.models import UserProfile
from django.db import models


class PoolConsultant(models.Model):
    consultant = models.ForeignKey(
        UserProfile,
        related_name="enlisted_in_record_pool",
        on_delete=models.CASCADE,
        null=False,
    )
    enlisted = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "PoolConsultant"
        verbose_name_plural = "PoolConsultants"

    def __str__(self):
        return "poolConsultant: {}; consultant: {};".format(
            self.pk, self.consultant.email
        )
