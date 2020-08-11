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
from backend.static.notification_enums import NotificationGroupType, NotificationType


class NotificationManager(models.Manager):
    """
    Manager for Notifications
    provides methods for whole query table and 'static' class methods
    """

    @staticmethod
    def create_notification(user: UserProfile, source_user: UserProfile, ref_id: str, ref_text: str,
                            notification_group_type: NotificationGroupType, notification_type: NotificationType):
        try:
            group = NotificationGroup.objects.get(user=user, type=notification_group_type.value, ref_id=str(ref_id))
        except Exception as e:
            group = NotificationGroup(user=user, type=notification_group_type.value, ref_id=str(ref_id),
                                      ref_text=ref_text)
            group.save()
        notification = Notification(notification_group=group, source_user=source_user, type=notification_type.value)
        notification.save()

    @staticmethod
    def create_notification_new_record_message(user: UserProfile, source_user: UserProfile, record: 'EncrypedRecord'):
        Notification.objects.create_notification(user, source_user, str(record.id), record.record_token,
                                                 NotificationGroupType.RECORD,
                                                 NotificationType.RECORD__RECORD_MESSAGE_ADDED)

    @staticmethod
    def create_notification_new_record(user: UserProfile, source_user: UserProfile, record: 'EncryptedRecord'):
        Notification.objects.create_notification(user=user, source_user=source_user, ref_id=str(record.id),
                                                 ref_text=record.record_token,
                                                 notification_group_type=NotificationGroupType.RECORD,
                                                 notification_type=NotificationType.RECORD__CREATED)

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

    type = models.CharField(max_length=75, choices=NotificationType.choices(), null=False, default="")
    read = models.BooleanField(default=False, null=False)

    text = models.TextField(null=True)

    objects = NotificationManager()

    def __str__(self):
        return 'notification: ' + str(self.id)

    def save(self, *args, **kwargs):
        super().save()
        self.notification_group.new_activity()
