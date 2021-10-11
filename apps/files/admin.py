from apps.files.models import File, Folder, FolderPermission, PermissionForFolder
from django.contrib import admin


class FileAdmin(admin.ModelAdmin):
    model = File
    list_display = ('name', 'key', 'exists', 'created')

    def get_form(self, request, obj=None, **kwargs):
        form = super(FileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['key'].widget.attrs['style'] = 'width: 900px;'
        return form


admin.site.register(File, FileAdmin)
admin.site.register(Folder)
admin.site.register(FolderPermission)
admin.site.register(PermissionForFolder)
