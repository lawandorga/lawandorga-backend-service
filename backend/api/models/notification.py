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

from backend.api.models import NotificationGroup, UserProfile
from backend.static.notification_enums import NotificationEvent, NotificationGroupType, NotificationType


class NotificationManager(models.Manager):
    """
    Manager for Notifications
    provides methods for whole query table and 'static' class methods
    """

    @staticmethod
    def create_notification(event: NotificationEvent, event_subject: NotificationType, ref_id: int,
                            user: UserProfile, source_user: UserProfile, ref_text: str, read: bool):
        pass
        # notification = Notification(event=event, event_type=event_subject, ref_id=ref_id, user=user,
        #                             source_user=source_user, ref_text=ref_text, read=read)
        # notification.save()

    @staticmethod
    def create_notification_new_record_message(user: UserProfile, source_user: UserProfile, record: 'EncrypedRecord'):
        try:
            group = NotificationGroup.objects.get(user=user, type=NotificationGroupType.RECORD.value,
                                                  ref_id=str(record.id))
        except Exception as e:
            group = NotificationGroup(user=user, type=NotificationGroupType.RECORD.value, ref_id=str(record.id),
                                      ref_text=record.record_token)
            group.save()
        notification = Notification(notification_group=group, source_user=source_user,
                                    event=NotificationEvent.CREATED.value,
                                    sub_type=NotificationType.RECORD_MESSAGE.value)
        notification.save()

        # notification = Notification(event_subject=NotificationEventSubject.RECORD_MESSAGE,
        #                             event=NotificationEvent.CREATED, ref_id=str(record.id), user=user,
        #                             source_user=source_user, ref_text=record.record_token)
        # notification.save()

    @staticmethod
    def create_notification_new_record(user: UserProfile, source_user: UserProfile, record: 'EncryptedRecord'):
        pass
        # notification = Notification(event_subject=NotificationEventSubject.RECORD,
        #                             event=NotificationEvent.CREATED, ref_id=str(record.id), user=user,
        #                             source_user=source_user, ref_text=record.record_token)
        # notification.save()

    @staticmethod
    def create_notification_added_to_group(user: UserProfile, source_user: UserProfile, group: 'Group'):
        pass
        # notification = Notification(event_subject=NotificationEventSubject.GROUP,
        #                             event=NotificationEvent.ADDED, ref_id=str(group.id), user=user,
        #                             source_user=source_user, ref_text=group.name)
        # notification.save()

    @staticmethod
    def create_notification_removed_from_group(user: UserProfile, source_user: UserProfile, group: 'Group'):
        pass
        # notification = Notification(event_subject=NotificationEventSubject.GROUP,
        #                             event=NotificationEvent.REMOVED, ref_id=str(group.id), user=user,
        #                             source_user=source_user, ref_text=group.name)
        # notification.save()


class Notification(models.Model):
    notification_group = models.ForeignKey(NotificationGroup, related_name="notifications", on_delete=models.CASCADE,
                                           null=True)
    source_user = models.ForeignKey(UserProfile, related_name="notification_caused", on_delete=models.SET_NULL,
                                    null=True)
    created = models.DateTimeField(auto_now_add=True)

    event = models.CharField(max_length=50, choices=NotificationEvent.choices(), null=False)
    sub_type = models.CharField(max_length=50, choices=NotificationType.choices(), null=False, default="")
    read = models.BooleanField(default=False, null=False)

    text = models.TextField(null=True)

    objects = NotificationManager()

    def __str__(self):
        return 'notification: ' + str(self.id)

    def save(self, *args, **kwargs):
        super().save()
        self.notification_group.new_activity()
