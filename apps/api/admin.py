from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.api.models import UserProfile, Notification, Permission, HasPermission, Rlc, UserEncryptionKeys, \
    RlcEncryptionKeys, UsersRlcKeys, NotificationGroup, Group, LoggedPath, RlcUser
from django.contrib import admin


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', )}),
        (_('Personal info'), {'fields': ('name', )}),
        (_('Permissions'), {
            'fields': ('groups', ),
        }),
        (_('RLC Stuff'), {
            'fields': ('rlc', ),
        }),
        (_('Important dates'), {'fields': ('last_login', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name')
    search_fields = ('name', 'email')
    ordering = ('email',)
    list_filter = ()


class HasPermissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user_has_permission']


class RlcUserAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'user__name')


class LoggedPathAdmin(admin.ModelAdmin):
    search_fields = ('path', 'user__email')


class UsersRlcKeysAdmin(admin.ModelAdmin):
    search_fields = ('rlc__name', 'user__email')


admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(HasPermission, HasPermissionAdmin)
admin.site.register(Rlc)
admin.site.register(UserEncryptionKeys)
admin.site.register(RlcEncryptionKeys)
admin.site.register(UsersRlcKeys, UsersRlcKeysAdmin)
admin.site.register(NotificationGroup)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(Notification)
admin.site.register(LoggedPath, LoggedPathAdmin)
admin.site.register(RlcUser, RlcUserAdmin)
