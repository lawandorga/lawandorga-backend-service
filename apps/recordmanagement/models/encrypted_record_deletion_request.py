from django.utils import timezone

from apps.api.models import UserProfile, Rlc
from django.db import models


class EncryptedRecordDeletionRequest(models.Model):
    rlc = models.ForeignKey(Rlc, related_name='deletion_requests', on_delete=models.CASCADE, null=True, blank=True)  # remove null=True in the future
    record = models.ForeignKey(
        "EncryptedRecord",
        related_name="deletions_requested",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    request_from = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    request_processed = models.ForeignKey(
        UserProfile,
        related_name="e_record_deletion_request_processed",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    explanation = models.TextField(default="", blank=True)
    requested = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True, blank=True)

    record_deletion_request_states_possible = (
        ("re", "requested"),
        ("gr", "granted"),
        ("de", "declined"),
    )
    state = models.CharField(
        max_length=2, choices=record_deletion_request_states_possible, default="re"
    )

    def __str__(self):
        return "recordDeletionRequest: {}; requested: {};".format(
            self.pk, self.requested
        )

    class Meta:
        verbose_name = 'EncryptedRecordDeletionRequest'
        verbose_name_plural = 'EncryptedRecordDeletionRequests'
        ordering = ['-state', '-requested']

    def save(self, *args, **kwargs):
        if self.rlc is None and self.request_from:
            self.rlc = self.request_from.rlc
        elif self.rlc is None and self.record:
            self.rlc = self.record.from_rlc
        super().save(*args, **kwargs)
        if self.state == 'gr' and self.record:
            EncryptedRecordDeletionRequest.objects.filter(record=self.record, state="re") \
                .update(state='gr', processed_on=timezone.now())
            self.processed_on = timezone.now()
            super().save()
            self.record.delete()
