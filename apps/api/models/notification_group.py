#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2020  Dominik Walser
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
from apps.static.notification_enums import NotificationGroupType
from apps.api.models.user import UserProfile
from django.utils import timezone
from django.db import models


class NotificationGroup(models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="notification_groups", on_delete=models.CASCADE
    )
    last_activity = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now)

    type = models.CharField(
        max_length=100, choices=NotificationGroupType.choices(), null=False
    )
    read = models.BooleanField(default=False, null=False)

    ref_id = models.CharField(max_length=50, null=False)
    ref_text = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = "NotificationGroup"
        verbose_name_plural = "NotificationGroups"

    def __str__(self):
        return "notificationGroup: {}; user: {};".format(self.pk, self.user.email)

    def new_activity(self):
        self.last_activity = timezone.now()
        self.read = False
        self.save()

    def all_notifications_read(self) -> bool:
        return (
            self.notifications.count() > 0
            and self.notifications.filter(read=False).count() == 0
        )
