from django.contrib import admin

from core.records.models.deletion import RecordsDeletion
from core.records.models.record import RecordsRecord
from core.records.models.setting import RecordsView

admin.site.register(RecordsRecord)
admin.site.register(RecordsView)
admin.site.register(RecordsDeletion)
