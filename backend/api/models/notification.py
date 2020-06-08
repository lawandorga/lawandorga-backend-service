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

from enum import Enum

from django.db import models

from backend.api.models import UserProfile


class NotificationEventTypes(Enum):
    RECORD = 1
    RECORD_MESSAGE = 2
    RECORD_DOCUMENT = 3
    RECORD_PERMISSION_REQUEST = 4
    GROUP = 5
    FILE = 6


class NotificationEvents(Enum):
    CREATED = 1
    DELETED = 2
    MOVED = 3
    UPDATED = 4
    ADDED = 5


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, related_name="notifications", on_delete=models.CASCADE)
    # message = models.CharField(max_length=2048)
    source_user = models.ForeignKey(UserProfile, related_name="notification_caused", on_delete=models.SET_NULL,
                                    null=True)
    event_subject = models.CharField(max_length=50, null=False)
    event = models.CharField(max_length=50, null=False)
    ref_id = models.CharField(max_length=50, null=False)

    @staticmethod
    def add_notification(event, event_subject, ref_id, user, source_user):
        notification = Notification(event=event, event_type=event_subject, ref_id=ref_id, user=user,
                                    source_user=source_user)
        notification.save()

    @staticmethod
    def add_notification_new_record_message(ref_id, user, source_user):
        notification = Notification(event_subject=NotificationEventTypes.RECORD_MESSAGE,
                                    event=NotificationEvents.CREATED, ref_id=ref_id, user=user, source_user=source_user)
        notification.save()
