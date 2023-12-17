from django.contrib import admin

from core.questionnaires.models import (
    Questionnaire,
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireTemplate,
    QuestionnaireTemplateFile,
)


class QuestionnaireAdmin(admin.ModelAdmin):
    model = Questionnaire
    list_display = ("id", "name", "folder_uuid", "org_name", "created", "updated")
    list_filter = ("name", "folder_uuid", "created", "updated")


class QuestionnaireAnswerAdmin(admin.ModelAdmin):
    model = QuestionnaireAnswer
    list_display = ("__str__", "questionnaire", "field", "created", "updated")
    search_fields = ("questionnaire__pk", "field__pk")


admin.site.register(QuestionnaireTemplate)
admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(QuestionnaireQuestion)
admin.site.register(QuestionnaireAnswer, QuestionnaireAnswerAdmin)
admin.site.register(QuestionnaireTemplateFile)
