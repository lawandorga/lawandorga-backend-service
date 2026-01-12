from django.contrib import admin

from core.data_sheets.models import (
    DataSheet,
    DataSheetEncryptedFileEntry,
    DataSheetEncryptedFileField,
    DataSheetEncryptedSelectEntry,
    DataSheetEncryptedSelectField,
    DataSheetEncryptedStandardEntry,
    DataSheetEncryptedStandardField,
    DataSheetMultipleEntry,
    DataSheetMultipleField,
    DataSheetSelectEntry,
    DataSheetSelectField,
    DataSheetStandardEntry,
    DataSheetStandardField,
    DataSheetStateEntry,
    DataSheetStateField,
    DataSheetTemplate,
    DataSheetUsersEntry,
    DataSheetUsersField,
)
from core.data_sheets.models.data_sheet import DataSheetStatisticEntry
from core.data_sheets.models.template import DataSheetStatisticField

admin.site.register(DataSheetTemplate)
admin.site.register(DataSheet)

admin.site.register(DataSheetStandardField)
admin.site.register(DataSheetSelectField)
admin.site.register(DataSheetUsersField)
admin.site.register(DataSheetStateField)
admin.site.register(DataSheetMultipleField)
admin.site.register(DataSheetEncryptedSelectField)
admin.site.register(DataSheetEncryptedFileField)
admin.site.register(DataSheetEncryptedStandardField)
admin.site.register(DataSheetStatisticField)

admin.site.register(DataSheetStandardEntry)
admin.site.register(DataSheetStateEntry)
admin.site.register(DataSheetSelectEntry)
admin.site.register(DataSheetUsersEntry)
admin.site.register(DataSheetMultipleEntry)
admin.site.register(DataSheetEncryptedSelectEntry)
admin.site.register(DataSheetEncryptedFileEntry)
admin.site.register(DataSheetEncryptedStandardEntry)
admin.site.register(DataSheetStatisticEntry)
