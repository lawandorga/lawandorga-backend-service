from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from core.auth.models.mfa import MultiFactorAuthenticationSecret
from core.auth.models.session import CustomSession

from .models import InternalUser, MatrixUser, OrgUser, StatisticUser, UserProfile


class UserAdmin(DjangoUserAdmin):
    fieldsets = [
        (None, {"fields": ("email",)}),
        (_("Personal info"), {"fields": ("name",)}),
        (  # type: ignore
            _("Permissions"),
            {
                "fields": ("groups",),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
        (_("Other"), {"fields": ("is_superuser",)}),
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


class CustomSessionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "user_id", "expire_date")
    search_fields = ("session_key", "user_id")
    list_filter = ("expire_date",)


admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(OrgUser, RlcUserAdmin)
admin.site.register(StatisticUser, StatisticUserAdmin)
admin.site.register(MatrixUser, MatrixUserAdmin)
admin.site.register(MultiFactorAuthenticationSecret)
admin.site.register(CustomSession, CustomSessionAdmin)
