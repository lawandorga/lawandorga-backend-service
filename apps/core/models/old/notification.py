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
from django.db import models
from django.utils import timezone

from .notification_group import NotificationGroup
from .. import UserProfile
from apps.static.notification_enums import NotificationType


class Notification(models.Model):
    notification_group = models.ForeignKey(
        NotificationGroup,
        related_name="notifications",
        on_delete=models.CASCADE,
        null=True,
    )
    source_user = models.ForeignKey(
        UserProfile,
        related_name="notification_caused",
        on_delete=models.SET_NULL,
        null=True,
    )
    created = models.DateTimeField(default=timezone.now)
    type = models.CharField(
        max_length=75, choices=NotificationType.choices(), null=False, default=""
    )
    read = models.BooleanField(default=False, null=False)
    text = models.TextField(null=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return "notification: {};".format(self.id)

    def save(self, *args, **kwargs):
        if not self.read and self.id is None:
            self.notification_group.new_activity()
        super().save()
        all_in_group_read = self.notification_group.all_notifications_read()
        if all_in_group_read and not self.notification_group.read:
            self.notification_group.read = True
            self.notification_group.save()
        elif not all_in_group_read and self.notification_group.read:
            self.notification_group.read = False
            self.notification_group.save()
