from django.contrib import admin

from apps.core.records.models import (
    EncryptedClient,
    EncryptedRecordDocument,
    EncryptedRecordMessage,
    PoolConsultant,
    PoolRecord,
    Questionnaire,
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireTemplate,
    QuestionnaireTemplateFile,
    Record,
    RecordAccess,
    RecordDeletion,
    RecordEncryptedFileEntry,
    RecordEncryptedFileField,
    RecordEncryptedSelectEntry,
    RecordEncryptedSelectField,
    RecordEncryptedStandardEntry,
    RecordEncryptedStandardField,
    RecordEncryptionNew,
    RecordMultipleEntry,
    RecordMultipleField,
    RecordSelectEntry,
    RecordSelectField,
    RecordStandardEntry,
    RecordStandardField,
    RecordStateEntry,
    RecordStateField,
    RecordTemplate,
    RecordUsersEntry,
    RecordUsersField,
)

admin.site.register(EncryptedClient)
admin.site.register(EncryptedRecordDocument)
admin.site.register(EncryptedRecordMessage)
admin.site.register(RecordAccess)
admin.site.register(RecordDeletion)
admin.site.register(PoolConsultant)
admin.site.register(PoolRecord)
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
