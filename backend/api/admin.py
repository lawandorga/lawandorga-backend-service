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
from backend.api.models import UserProfile, Notification, Permission, HasPermission, Rlc, \
    NewUserRequest, UserEncryptionKeys, RlcEncryptionKeys, UsersRlcKeys, RlcSettings, \
    NotificationGroup, UserActivityPath, UserSession, UserSessionPath, Group
from django.contrib import admin

admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(HasPermission)
admin.site.register(Rlc)
admin.site.register(NewUserRequest)
admin.site.register(UserEncryptionKeys)
admin.site.register(RlcEncryptionKeys)
admin.site.register(UsersRlcKeys)
admin.site.register(RlcSettings)
admin.site.register(NotificationGroup)
admin.site.register(UserActivityPath)
admin.site.register(UserSession)
admin.site.register(UserSessionPath)
admin.site.register(UserProfile)
admin.site.register(Notification)
