from apps.static.encrypted_storage import EncryptedStorage
from apps.recordmanagement.models import EncryptedRecord
from django.core.files.storage import default_storage
from apps.api.models import Rlc
from django.conf import settings
from django.db import models
import uuid
import os


class Questionnaire(models.Model):
    name = models.CharField(max_length=100)
    rlc = models.ForeignKey(Rlc, related_name='questionnaires', on_delete=models.CASCADE, blank=True)
    notes = models.TextField(blank=True)
    records = models.ManyToManyField(EncryptedRecord, through='RecordQuestionnaire')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Questionnaire'
        verbose_name_plural = 'Questionnaire'

    def __str__(self):
        return 'questionnaire: {}; rlc: {};'.format(self.name, self.rlc.name)


class QuestionnaireField(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='fields', on_delete=models.CASCADE)
    TYPE_CHOICES = (
        ('FILE', 'File'),
        ('TEXTAREA', 'Text'),
    )
    question = models.CharField(max_length=100)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'QuestionnaireField'
        verbose_name_plural = 'QuestionnaireFields'

    def __str__(self):
        return 'questionnaireField: {};'.format(self.pk)

    @property
    def name(self):
        return '{}_{}'.format(self.type.lower(), self.id)


class RecordQuestionnaire(models.Model):
    record = models.ForeignKey(EncryptedRecord, on_delete=models.CASCADE, related_name='questionnaires')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT, related_name='record_questionnaires')
    code = models.SlugField(unique=True, blank=True)
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


class QuestionnaireAnswer(models.Model):
    record_questionnaire = models.ForeignKey(RecordQuestionnaire, on_delete=models.CASCADE, related_name='answers')
    field = models.ForeignKey(QuestionnaireField, on_delete=models.CASCADE, related_name='answers')
    data = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'QuestionnaireAnswer'
        verbose_name_plural = 'QuestionnaireAnswers'

    def __str__(self):
        return 'questionnaireAnswer: {};'.format(self.pk)

    def slugify(self, unique=0):
        key = 'rlcs/{}/record_questionnaires/{}/{}-{}'.format(self.record_questionnaire.questionnaire.rlc.pk,
                                                              self.record_questionnaire.id, self.field.id, unique)
        if not QuestionnaireAnswer.objects.filter(data=key).exists():
            return key
        else:
            unique = unique + 1
            return self.slugify(unique=unique)

    def upload_file(self, file):
        local_file_path = default_storage.save(self.data, file)
        global_file_path = os.path.join(settings.MEDIA_ROOT, local_file_path)
        EncryptedStorage.upload_to_s3(global_file_path, self.data)
        default_storage.delete(self.data)

    def set_data(self, data, *args):
        if self.field.type == 'FILE':
            file = data
            self.data = '{}/{}'.format(self.slugify(), file.name)
            self.save()
            self.upload_file(file)
        if self.field.type == 'TEXTAREA':
            self.data = data
            self.save()
