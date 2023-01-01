from django.contrib import admin

from core.questionnaires.models import (
    Questionnaire,
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireTemplate,
    QuestionnaireTemplateFile,
)

admin.site.register(QuestionnaireTemplate)
admin.site.register(Questionnaire)
admin.site.register(QuestionnaireQuestion)
admin.site.register(QuestionnaireAnswer)
admin.site.register(QuestionnaireTemplateFile)
