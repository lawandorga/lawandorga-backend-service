from apps.api.models import Rlc, UserProfile
from django.utils import timezone
from django.db import models


class TextDocument(models.Model):
    rlc = models.ForeignKey(Rlc, related_name="text_documents", null=False, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(UserProfile, related_name="text_documents_created", on_delete=models.SET_NULL,
                                null=True)

    class Meta:
        verbose_name = 'TextDocument'
        verbose_name_plural = 'TextDocuments'

    def __str__(self):
        return 'textDocument: {};'.format(self.pk)
