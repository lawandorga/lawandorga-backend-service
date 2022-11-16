from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import InternalUser, MatrixUser, RlcUser, StatisticUser, UserProfile


class UserAdmin(DjangoUserAdmin):
    fieldsets = [
        (None, {"fields": ("email",)}),
        (_("Personal info"), {"fields": ("name",)}),  # type: ignore
        (  # type: ignore
            _("Permissions"),
            {
                "fields": ("groups",),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),  # type: ignore
    ]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "name")
    search_fields = ("name", "email")
    ordering = ("email",)
    list_filter = ()


class RlcUserAdmin(admin.ModelAdmin):
    search_fields = ("user__email", "user__name")


class StatisticUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


class InternalUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


class MatrixUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(RlcUser, RlcUserAdmin)
admin.site.register(StatisticUser, StatisticUserAdmin)
admin.site.register(MatrixUser, MatrixUserAdmin)
