from apps.recordmanagement.models import OriginCountry, EncryptedRecord, RecordEncryption, \
    EncryptedClient, EncryptedRecordDocument, EncryptedRecordMessage, RecordAccess, \
    RecordDeletion, PoolConsultant, PoolRecord, Questionnaire, QuestionnaireTemplate, \
    QuestionnaireQuestion, QuestionnaireAnswer, QuestionnaireTemplateFile, Record, RecordSelectField, \
    RecordStandardField, RecordTemplate, RecordUsersField, RecordStateField, RecordMultipleField, \
    RecordEncryptedSelectField, RecordEncryptedFileField, RecordEncryptedStandardField, RecordStandardEntry, \
    RecordStateEntry, RecordSelectEntry, RecordUsersEntry, RecordMultipleEntry, RecordEncryptedSelectEntry, \
    RecordEncryptedFileEntry, RecordEncryptedStandardEntry, RecordEncryptionNew
from django.contrib import admin

admin.site.register(OriginCountry)
admin.site.register(RecordEncryption)
admin.site.register(EncryptedClient)
admin.site.register(EncryptedRecordDocument)
admin.site.register(EncryptedRecordMessage)
admin.site.register(RecordAccess)
admin.site.register(RecordDeletion)
admin.site.register(PoolConsultant)
admin.site.register(PoolRecord)
admin.site.register(EncryptedRecord)
admin.site.register(QuestionnaireTemplate)
admin.site.register(Questionnaire)
admin.site.register(QuestionnaireQuestion)
admin.site.register(QuestionnaireAnswer)
admin.site.register(QuestionnaireTemplateFile)

admin.site.register(RecordTemplate)
admin.site.register(Record)
admin.site.register(RecordEncryptionNew)

admin.site.register(RecordStandardField)
admin.site.register(RecordSelectField)
admin.site.register(RecordUsersField)
admin.site.register(RecordStateField)
admin.site.register(RecordMultipleField)
admin.site.register(RecordEncryptedSelectField)
admin.site.register(RecordEncryptedFileField)
admin.site.register(RecordEncryptedStandardField)

admin.site.register(RecordStandardEntry)
admin.site.register(RecordStateEntry)
admin.site.register(RecordSelectEntry)
admin.site.register(RecordUsersEntry)
admin.site.register(RecordMultipleEntry)
admin.site.register(RecordEncryptedSelectEntry)
admin.site.register(RecordEncryptedFileEntry)
admin.site.register(RecordEncryptedStandardEntry)
