from typing import TYPE_CHECKING, Literal

from django.db import models

from core.models import Org

if TYPE_CHECKING:
    from core.questionnaires.models.questionnaire import Questionnaire


class QuestionnaireTemplate(models.Model):
    @classmethod
    def create(cls, name: str, org: Org, notes="") -> "QuestionnaireTemplate":
        template = QuestionnaireTemplate(name=name, rlc=org, notes=notes)
        return template

    name = models.CharField(max_length=100)
    rlc = models.ForeignKey(
        Org, related_name="questionnaire_templates", on_delete=models.CASCADE, blank=True
    )
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        questionnaires: models.QuerySet["Questionnaire"]
        fields: models.QuerySet["QuestionnaireQuestion"]
        files: models.QuerySet["QuestionnaireTemplateFile"]
        rlc_id: int

    class Meta:
        verbose_name = "QUE_Template"
        verbose_name_plural = "QUE_Templates"

    def __str__(self):
        return "questionnaire: {}; rlc: {};".format(self.name, self.rlc.name)

    def add_question(
        self, question_type: Literal["FILE", "TEXTAREA"], question: str, order=1
    ) -> "QuestionnaireQuestion":
        q = QuestionnaireQuestion(
            type=question_type, question=question, order=order, questionnaire=self
        )
        return q

    def get_question(self, question_id: int) -> "QuestionnaireQuestion":
        return self.fields.get(id=question_id)

    def update_question(
        self,
        question_id: int,
        question_type: Literal["FILE", "TEXTAREA"],
        question: str,
        order=1,
    ) -> "QuestionnaireQuestion":
        q = self.get_question(question_id)
        q.update(question_type, question, order)
        return q

    def update(self, name: str | None, notes: str | None):
        if name is not None:
            self.name = name
        if notes is not None:
            self.notes = notes

    def add_file(self, name: str, file) -> None:
        f = QuestionnaireTemplateFile(name=name, questionnaire=self)
        f.save()
        filename = f"{name}.{file.name.split('.')[-1]}"
        f.file.save(filename, file)

    def get_file(self, file_id: int) -> "QuestionnaireTemplateFile":
        f = self.files.get(id=file_id)
        return f


class QuestionnaireTemplateFile(models.Model):
    questionnaire = models.ForeignKey(
        QuestionnaireTemplate, on_delete=models.CASCADE, related_name="files"
    )
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="questionnairefile/")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "QUE_TemplateFile"
        verbose_name_plural = "QUE_TemplateFiles"

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
        verbose_name = "QUE_TemplateField"
        verbose_name_plural = "QUE_TemplateFields"

    def __str__(self):
        return "questionnaireField: {};".format(self.pk)

    @property
    def name(self):
        return "{}_{}".format(self.type.lower(), self.pk)

    def update(
        self, question_type: Literal["FILE", "TEXTAREA"], question: str, order=1
    ):
        self.question = question
        self.type = question_type
        self.order = order
