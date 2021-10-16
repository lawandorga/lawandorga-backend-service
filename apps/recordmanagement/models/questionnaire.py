import uuid

from apps.recordmanagement.models import EncryptedRecord
from apps.api.models import Rlc
from django.db import models


class Questionnaire(models.Model):
    name = models.CharField(max_length=100)
    rlc = models.ForeignKey(Rlc, related_name='questionnaires', on_delete=models.CASCADE, blank=True)
    notes = models.TextField(blank=True)
    questionnaire = models.TextField()
    allow_file_upload = models.BooleanField(default=True)
    records = models.ManyToManyField(EncryptedRecord, through='RecordQuestionnaire')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Questionnaire'
        verbose_name_plural = 'Questionnaire'

    def __str__(self):
        return 'questionnaire: {}; rlc: {};'.format(self.name, self.rlc.name)


class RecordQuestionnaire(models.Model):
    record = models.ForeignKey(EncryptedRecord, on_delete=models.CASCADE, related_name='questionnaires')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT, related_name='record_questionnaires')
    answer = models.TextField(blank=True)
    answered = models.BooleanField(default=False)
    code = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'RecordQuestionnaire'
        verbose_name_plural = 'RecordQuestionnaires'

    def __str__(self):
        return 'recordQuestionnaire: {};'.format(self.pk)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:6].upper()
        super().save(*args, **kwargs)
