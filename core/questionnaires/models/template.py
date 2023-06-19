from typing import Literal

from django.db import models

from core.models import Org


class QuestionnaireTemplate(models.Model):
    @classmethod
    def create(cls, name: str, org: Org, notes="") -> "QuestionnaireTemplate":
        template = QuestionnaireTemplate(name=name, rlc=org, notes=notes)
        return template

    name = models.CharField(max_length=100)
    rlc = models.ForeignKey(
        Org, related_name="questionnaires", on_delete=models.CASCADE, blank=True
    )
    notes = models.TextField(blank=True)
    records = models.ManyToManyField("Record", through="Questionnaire")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaire"

    def __str__(self):
        return "questionnaire: {}; rlc: {};".format(self.name, self.rlc.name)

    def add_question(
        self, question_type: Literal["FILE", "TEXTAREA"], question: str, order=1
    ) -> "QuestionnaireQuestion":
        q = QuestionnaireQuestion(
            type=question_type, question=question, order=order, questionnaire=self
        )
        return q

    def update(self, name: str | None, notes: str | None):
        if name is not None:
            self.name = name
        if notes is not None:
            self.notes = notes


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
