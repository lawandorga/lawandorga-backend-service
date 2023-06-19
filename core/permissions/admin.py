from django.contrib import admin

from .models import HasPermission, Permission


class HasPermissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


admin.site.register(Permission)
admin.site.register(HasPermission, HasPermissionAdmin)
