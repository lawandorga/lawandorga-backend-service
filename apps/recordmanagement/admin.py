from apps.recordmanagement.models import OriginCountry, RecordDocumentTag, EncryptedRecord, RecordEncryption, \
    EncryptedClient, EncryptedRecordDocument, EncryptedRecordMessage, EncryptedRecordPermission, \
    EncryptedRecordDeletionRequest, PoolConsultant, PoolRecord
from django.contrib import admin

admin.site.register(OriginCountry)
admin.site.register(RecordDocumentTag)
admin.site.register(RecordEncryption)
admin.site.register(EncryptedClient)
admin.site.register(EncryptedRecordDocument)
admin.site.register(EncryptedRecordMessage)
admin.site.register(EncryptedRecordPermission)
admin.site.register(EncryptedRecordDeletionRequest)
admin.site.register(PoolConsultant)
admin.site.register(PoolRecord)
admin.site.register(EncryptedRecord)
