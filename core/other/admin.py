from django.contrib import admin

from .models import LoggedPath


class LoggedPathAdmin(admin.ModelAdmin):
    search_fields = ("path", "user__email", "status")


admin.site.register(LoggedPath, LoggedPathAdmin)
