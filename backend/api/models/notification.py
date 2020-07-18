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


class NotificationEventObject(Enum):
    """
    Enum for notification event object
    these regard the models which the notification is about
    """
    RECORD = "RECORD"
    RECORD_MESSAGE = "RECORD_MESSAGE"
    RECORD_DOCUMENT = "RECORD_DOCUMENT"
    RECORD_PERMISSION_REQUEST = "RECORD_PERMISSION_REQUEST"
    GROUP = "GROUP"
    FILE = "FILE"


class NotificationEventType(Enum):
    """
    enum for notification events types
    contains the action which was performed
    """
    CREATED = "CREATED"
    DELETED = "DELETED"
    MOVED = "MOVED"
    UPDATED = "UPDATED"
    ADDED = "ADDED"


class NotificationManager(models.Manager):
    """
    Manager for Notifications
    provides methods for whole query table and 'static' class methods
    """

    @staticmethod
    def create_notification(event: NotificationEventType, event_subject: NotificationEventObject, ref_id: int,
                            user: UserProfile, source_user: UserProfile, ref_text: str, read: bool):
        notification = Notification(event=event, event_type=event_subject, ref_id=ref_id, user=user,
                                    source_user=source_user, ref_text=ref_text, read=read)
        notification.save()

    @staticmethod
    def create_notification_new_record_message(ref_id: str, user: UserProfile, source_user: UserProfile, ref_text: str):
        notification = Notification(event_subject=NotificationEventObject.RECORD_MESSAGE,
                                    event=NotificationEventType.CREATED, ref_id=ref_id, user=user,
                                    source_user=source_user, ref_text=ref_text)
        notification.save()

    @staticmethod
    def create_notification_new_record(ref_id: str, user: UserProfile, source_user: UserProfile, ref_text: str):
        notification = Notification(event_subject=NotificationEventObject.RECORD,
                                    event=NotificationEventType.CREATED, ref_id=ref_id, user=user,
                                    source_user=source_user, ref_text=ref_text)
        notification.save()


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, related_name="notifications", on_delete=models.CASCADE)
    source_user = models.ForeignKey(UserProfile, related_name="notification_caused", on_delete=models.SET_NULL,
                                    null=True)

    event_subject = models.CharField(max_length=50, null=False)
    event = models.CharField(max_length=50, null=False)
    ref_id = models.CharField(max_length=50, null=False)
    ref_text = models.CharField(max_length=100, null=True)
    read = models.BooleanField(default=False, null=False)

    objects = NotificationManager()

    def __str__(self):
        return 'notification: ' + str(self.id)
