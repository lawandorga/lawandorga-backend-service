from django.contrib import admin

from .models import LoggedPath


class LoggedPathAdmin(admin.ModelAdmin):
    search_fields = ("path", "user__email", "status")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


admin.site.register(LoggedPath, LoggedPathAdmin)
