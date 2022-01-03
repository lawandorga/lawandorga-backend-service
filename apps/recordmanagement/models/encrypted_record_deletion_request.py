from apps.recordmanagement.models.record import Record
from apps.api.models import UserProfile, Rlc
from django.utils import timezone
from django.db import models


class EncryptedRecordDeletionRequest(models.Model):
    old_record = models.ForeignKey("EncryptedRecord", on_delete=models.SET_NULL, null=True, blank=True, db_index=False)
    record = models.ForeignKey(Record, related_name='deletions', on_delete=models.CASCADE, null=True)
    request_from = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='requestedrecorddeletions')
    request_processed = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='processedrecorddeletions')
    explanation = models.TextField(default="", blank=True)
    processed_on = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    STATE_CHOICES = (
        ("re", "requested"),
        ("gr", "granted"),
        ("de", "declined"),
    )
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default="re")

    def __str__(self):
        return "recordDeletionRequest: {}; requested: {};".format(self.pk, self.state)

    class Meta:
        verbose_name = 'EncryptedRecordDeletionRequest'
        verbose_name_plural = 'EncryptedRecordDeletionRequests'
        ordering = ['-state', '-created']

    def save(self, *args, **kwargs):
        if self.state == 'gr' and self.record:
            self.processed_on = timezone.now()
            super().save(*args, **kwargs)
            self.record.delete()
        else:
            super().save(*args, **kwargs)
