from apps.recordmanagement.models import OriginCountry, EncryptedRecord, RecordEncryption, \
    EncryptedClient, EncryptedRecordDocument, EncryptedRecordMessage, EncryptedRecordPermission, \
    EncryptedRecordDeletionRequest, PoolConsultant, PoolRecord, Questionnaire, QuestionnaireTemplate, \
    QuestionnaireQuestion, QuestionnaireAnswer, QuestionnaireTemplateFile
from django.contrib import admin

admin.site.register(OriginCountry)
admin.site.register(RecordEncryption)
admin.site.register(EncryptedClient)
admin.site.register(EncryptedRecordDocument)
admin.site.register(EncryptedRecordMessage)
admin.site.register(EncryptedRecordPermission)
admin.site.register(EncryptedRecordDeletionRequest)
admin.site.register(PoolConsultant)
admin.site.register(PoolRecord)
admin.site.register(EncryptedRecord)
admin.site.register(QuestionnaireTemplate)
admin.site.register(Questionnaire)
admin.site.register(QuestionnaireQuestion)
admin.site.register(QuestionnaireAnswer)
admin.site.register(QuestionnaireTemplateFile)
