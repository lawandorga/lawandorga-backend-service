#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from backend.api.models import (
    UserProfile,
    Notification,
    Permission,
    HasPermission,
    Rlc,
    UserEncryptionKeys,
    RlcEncryptionKeys,
    UsersRlcKeys,
    NotificationGroup,
    Group, LoggedPath, RlcUser,
)
from django.contrib import admin


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', )}),
        (_('Personal info'), {'fields': ('name', )}),
        (_('Permissions'), {
            'fields': ('groups', ),
        }),
        (_('RLC Stuff'), {
            'fields': ('is_active', 'locked', 'email_confirmed', 'rlc', ),
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


admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(HasPermission, HasPermissionAdmin)
admin.site.register(Rlc)
admin.site.register(UserEncryptionKeys)
admin.site.register(RlcEncryptionKeys)
admin.site.register(UsersRlcKeys)
admin.site.register(NotificationGroup)
admin.site.register(UserProfile, UserAdmin)
admin.site.register(Notification)
admin.site.register(LoggedPath)
admin.site.register(RlcUser, RlcUserAdmin)
