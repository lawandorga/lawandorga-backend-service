import uuid

from django.db import models

from apps.api.models import Rlc
from apps.recordmanagement.models import EncryptedRecord, Record
from apps.static.encryption import (AESEncryption, EncryptedModelMixin,
                                    RSAEncryption)
from apps.static.storage import (download_and_decrypt_file,
                                 encrypt_and_upload_file)


class QuestionnaireTemplate(models.Model):
    name = models.CharField(max_length=100)
    rlc = models.ForeignKey(
        Rlc, related_name="questionnaires", on_delete=models.CASCADE, blank=True
    )
    notes = models.TextField(blank=True)
    records = models.ManyToManyField(EncryptedRecord, through="Questionnaire")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaire"

    def __str__(self):
        return "questionnaire: {}; rlc: {};".format(self.name, self.rlc.name)


class QuestionnaireTemplateFile(models.Model):
    questionnaire = models.ForeignKey(
        QuestionnaireTemplate, on_delete=models.CASCADE, related_name="files"
    )
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="questionnairefile/")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "QuestionnaireFile"
        verbose_name_plural = "QuestionnaireFiles"

    def __str__(self):
        return "questionnaireFile: {}; questionnaire: {};".format(
            self.name, self.questionnaire.name
        )


class QuestionnaireQuestion(models.Model):
    questionnaire = models.ForeignKey(
        QuestionnaireTemplate, related_name="fields", on_delete=models.CASCADE
    )
    TYPE_CHOICES = (
        ("FILE", "File"),
        ("TEXTAREA", "Text"),
    )
    question = models.CharField(max_length=100)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)
    order = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "QuestionnaireField"
        verbose_name_plural = "QuestionnaireFields"

    def __str__(self):
        return "questionnaireField: {};".format(self.pk)

    @property
    def name(self):
        return "{}_{}".format(self.type.lower(), self.id)


class Questionnaire(models.Model):
    old_record = models.ForeignKey(
        EncryptedRecord,
        on_delete=models.CASCADE,
        related_name="questionnaires",
        null=True,
    )
    record = models.ForeignKey(
        Record,
        on_delete=models.CASCADE,
        related_name="questionnaires",
        null=True,
        blank=True,
    )
    template = models.ForeignKey(
        QuestionnaireTemplate, on_delete=models.PROTECT, related_name="questionnaires"
    )
    code = models.SlugField(unique=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "RecordQuestionnaire"
        verbose_name_plural = "RecordQuestionnaires"

    def __str__(self):
        return "recordQuestionnaire: {};".format(self.pk)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:6].upper()
        super().save(*args, **kwargs)

    @property
    def answered(self):
        return self.answers.all().count() - self.template.fields.all().count() == 0


class QuestionnaireAnswer(EncryptedModelMixin, models.Model):
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name="answers"
    )
    field = models.ForeignKey(
        QuestionnaireQuestion, on_delete=models.CASCADE, related_name="answers"
    )
    data = models.BinaryField()
    aes_key = models.BinaryField(default=b"")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    encrypted_fields = ["data", "aes_key"]
    encryption_class = RSAEncryption

    class Meta:
        verbose_name = "QuestionnaireAnswer"
        verbose_name_plural = "QuestionnaireAnswers"

    def __str__(self):
        return "questionnaireAnswer: {};".format(self.pk)

    def encrypt(self, *args):
        key = self.questionnaire.template.rlc.get_public_key()
        super().encrypt(key)

    def decrypt(self, private_key_rlc=None, user=None, private_key_user=None):
        if user and private_key_user:
            private_key_rlc = self.questionnaire.template.rlc.get_private_key(
                user=user, private_key_user=private_key_user
            )
        elif private_key_rlc:
            pass
        else:
            raise ValueError(
                "You have to set (private_key_rlc) or (user and private_key_user)."
            )
        super().decrypt(private_key_rlc)

    def generate_key(self):
        key = "rlcs/{}/record_questionnaires/{}/{}/{}".format(
            self.questionnaire.template.rlc.pk,
            self.questionnaire.template.id,
            self.field.id,
            self.id,
        )
        return key

    def download_file(self, aes_key):
        file_key = "{}.enc".format(self.data)
        return download_and_decrypt_file(file_key, aes_key)

    def upload_file(self, file):
        self.aes_key = AESEncryption.generate_secure_key()
        self.data = "{}/{}".format(self.generate_key(), file.name)
        key = "{}.enc".format(self.data)
        encrypt_and_upload_file(file, key, self.aes_key)
