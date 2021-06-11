from backend.files.models import File, Folder, FolderPermission, PermissionForFolder
from django.contrib import admin


class FileAdmin(admin.ModelAdmin):
    model = File
    list_display = ('name', 'exists', 'created')


admin.site.register(File, FileAdmin)
admin.site.register(Folder)
admin.site.register(FolderPermission)
admin.site.register(PermissionForFolder)
