from django.db import models

from apps.api.models import UserProfile
from apps.recordmanagement.models.record import Record


class PoolConsultant(models.Model):
    consultant = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PoolConsultant"
        verbose_name_plural = "PoolConsultants"

    def __str__(self):
        return "poolConsultant: {}; consultant: {};".format(
            self.pk, self.consultant.email
        )


class PoolRecord(models.Model):
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    record_key = models.CharField(null=False, max_length=255)

    class Meta:
        verbose_name = "PoolRecord"
        verbose_name_plural = "PoolRecords"

    def __str__(self):
        return "poolRecord: {}; record: {};".format(self.pk, self.record.pk)
