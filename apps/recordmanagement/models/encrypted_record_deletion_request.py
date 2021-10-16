from apps.api.models import UserProfile
from django.db import models


class EncryptedRecordDeletionRequest(models.Model):
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
