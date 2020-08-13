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

from backend.api.models import UserProfile
from backend.static.notification_enums import NotificationGroupType


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

    def new_activity(self):
        self.last_activity = timezone.now()
        self.read = False
        self.save()

    def all_notifications_read(self) -> bool:
        return (
            self.notifications.count() > 0
            and self.notifications.filter(read=False).count() == 0
        )
