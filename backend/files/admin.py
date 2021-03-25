from backend.files.models import File, Folder, FolderPermission, PermissionForFolder
from django.contrib import admin

admin.site.register(File)
admin.site.register(Folder)
admin.site.register(FolderPermission)
admin.site.register(PermissionForFolder)
