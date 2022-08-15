from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from apps.core.forms import RlcAdminForm
from apps.core.models import (
    Article,
    CollabDocument,
    CollabPermission,
    File,
    Folder,
    FolderPermission,
    Group,
    HasPermission,
    HelpPage,
    ImprintPage,
    IndexPage,
    InternalUser,
    LoggedPath,
    OldUserEncryptionKeys,
    Org,
    OrgEncryption,
    Permission,
    PermissionForCollabDocument,
    PermissionForFolder,
    RlcUser,
    RoadmapItem,
    StatisticUser,
    TextDocumentVersion,
    TomsPage,
    UserProfile,
)

admin.site.register(CollabDocument)
admin.site.register(CollabPermission)
admin.site.register(PermissionForCollabDocument)
admin.site.register(TextDocumentVersion)


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email",)}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": ("groups",),
            },
        ),
        (
            _("RLC Stuff"),
            {
                "fields": ("rlc",),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
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


class HasPermissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user_has_permission"]


class RlcUserAdmin(admin.ModelAdmin):
    search_fields = ("user__email", "user__name")


class LoggedPathAdmin(admin.ModelAdmin):
    search_fields = ("path", "user__email", "status")


class UsersRlcKeysAdmin(admin.ModelAdmin):
    search_fields = ("rlc__name", "user__email")


class RlcAdmin(admin.ModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                ("LC", {"fields": ("name", "federal_state")}),
                ("Admin", {"fields": ("user_name", "user_email", "user_password")}),
            )
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = RlcAdminForm
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


class StatisticUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


class InternalUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]


admin.site.register(InternalUser, InternalUserAdmin)
admin.site.register(IndexPage, SingletonModelAdmin)
admin.site.register(ImprintPage, SingletonModelAdmin)
admin.site.register(TomsPage, SingletonModelAdmin)
admin.site.register(HelpPage, SingletonModelAdmin)
admin.site.register(RoadmapItem)
admin.site.register(Article)
admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(HasPermission, HasPermissionAdmin)
admin.site.register(Org, RlcAdmin)
admin.site.register(OldUserEncryptionKeys)
admin.site.register(OrgEncryption, UsersRlcKeysAdmin)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(LoggedPath, LoggedPathAdmin)
admin.site.register(RlcUser, RlcUserAdmin)
admin.site.register(StatisticUser, StatisticUserAdmin)


class FileAdmin(admin.ModelAdmin):
    model = File
    list_display = ("name", "key", "exists", "created")

    def get_form(self, request, obj=None, **kwargs):
        form = super(FileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["key"].widget.attrs["style"] = "width: 900px;"
        return form


class FolderAdmin(admin.ModelAdmin):
    model = Folder
    list_display = ("name", "parent_name", "same_parent", "rlc")
    search_fields = ("name", "pk", "rlc__pk", "rlc__name")
    list_per_page = 200
    autocomplete_fields = ("parent",)

    def parent_name(self, obj):
        return obj.parent.name if obj.parent else ""

    @admin.display(boolean=True)
    def same_parent(self, obj):
        return obj.pk == obj.parent_id


admin.site.register(File, FileAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(FolderPermission)
admin.site.register(PermissionForFolder)
