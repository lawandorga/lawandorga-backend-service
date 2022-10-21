from django.contrib import admin

from .models import LoggedPath, OldRlcEncryptionKeys, OldUserEncryptionKeys


class LoggedPathAdmin(admin.ModelAdmin):
    search_fields = ("path", "user__email", "status")


admin.site.register(OldUserEncryptionKeys)
admin.site.register(OldRlcEncryptionKeys)
admin.site.register(LoggedPath, LoggedPathAdmin)
