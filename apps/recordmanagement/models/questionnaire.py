from apps.static.encrypted_storage import EncryptedStorage
from apps.recordmanagement.models import EncryptedRecord
from django.core.files.storage import default_storage
from apps.static.encryption import EncryptedModelMixin, RSAEncryption, AESEncryption
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


class QuestionnaireFile(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='questionnairefile/')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'QuestionnaireFile'
        verbose_name_plural = 'QuestionnaireFiles'

    def __str__(self):
        return 'questionnaireFile: {}; questionnaire: {};'.format(self.name, self.questionnaire.name)


class QuestionnaireField(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='fields', on_delete=models.CASCADE)
    TYPE_CHOICES = (
        ('FILE', 'File'),
        ('TEXTAREA', 'Text'),
    )
    question = models.CharField(max_length=100)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
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


class QuestionnaireAnswer(EncryptedModelMixin, models.Model):
    record_questionnaire = models.ForeignKey(RecordQuestionnaire, on_delete=models.CASCADE, related_name='answers')
    field = models.ForeignKey(QuestionnaireField, on_delete=models.CASCADE, related_name='answers')
    data = models.BinaryField()
    aes_key = models.BinaryField(default=b'')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encrypted_fields = ['data', 'aes_key']
    encryption_class = RSAEncryption

    class Meta:
        verbose_name = 'QuestionnaireAnswer'
        verbose_name_plural = 'QuestionnaireAnswers'

    def __str__(self):
        return 'questionnaireAnswer: {};'.format(self.pk)

    def encrypt(self, *args):
        key = self.record_questionnaire.questionnaire.rlc.get_public_key()
        super().encrypt(key)

    def decrypt(self, private_key_rlc=None, user=None, private_key_user=None):
        if user and private_key_user:
            private_key_rlc = self.record_questionnaire.questionnaire.rlc \
                .get_private_key(user=user, private_key_user=private_key_user)
        elif private_key_rlc:
            pass
        else:
            raise ValueError("You have to set (private_key_rlc) or (user and private_key_user).")
        super().decrypt(private_key_rlc)

    def generate_key(self):
        key = 'rlcs/{}/record_questionnaires/{}/{}'.format(self.record_questionnaire.questionnaire.rlc.pk,
                                                           self.record_questionnaire.id, self.field.id)
        return key

    def download_file(self, aes_key):
        file_key = '{}.enc'.format(self.data)
        return EncryptedStorage.download_encrypted_file(file_key, aes_key)

    def upload_file(self, file):
        self.aes_key = AESEncryption.generate_secure_key()
        self.data = '{}/{}'.format(self.generate_key(), file.name)
        local_file_path = default_storage.save(self.data, file)
        global_file_path = os.path.join(settings.MEDIA_ROOT, local_file_path)
        EncryptedStorage.encrypt_file_and_upload_to_s3(global_file_path, self.aes_key, self.data)
        default_storage.delete(self.data)
