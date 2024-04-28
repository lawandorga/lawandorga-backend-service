from django.contrib import admin

from core.folders.models import FOL_ClosureTable, FOL_Folder

admin.site.register(FOL_Folder)
admin.site.register(FOL_ClosureTable)
