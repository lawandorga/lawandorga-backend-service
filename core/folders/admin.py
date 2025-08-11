from django.contrib import admin

from core.folders.models import FOL_ClosureTable, FOL_Folder


@admin.register(FOL_ClosureTable)
class FOLClosureTableAdmin(admin.ModelAdmin):
    search_fields = ["parent__id", "child__id", "parent__uuid", "child__uuid"]


admin.site.register(FOL_Folder)
