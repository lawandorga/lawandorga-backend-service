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


from backend.api.models import NotificationGroup, UserProfile
from backend.static.notification_enums import NotificationGroupType, NotificationType
from backend.static import permissions


class NotificationManager(models.Manager):
    """
    Manager for Notifications
    provides methods for whole query table and 'static' class methods
    """

    @staticmethod
    def create_notification(
        user: UserProfile,
        source_user: UserProfile,
        ref_id: str,
        ref_text: str,
        notification_group_type: NotificationGroupType,
        notification_type: NotificationType,
        text: str = "",
    ) -> (NotificationGroup, "Notification"):
        try:
            group = NotificationGroup.objects.get(
                user=user, type=notification_group_type.value, ref_id=str(ref_id)
            )
        except Exception as e:
            group = NotificationGroup(
                user=user,
                type=notification_group_type.value,
                ref_id=str(ref_id),
                ref_text=ref_text,
            )
            group.save()
        notification = Notification(
            notification_group=group,
            source_user=source_user,
            type=notification_type.value,
            text=text,
        )
        notification.save()
        return group, notification

    @staticmethod
    def create_notification_new_record_message(
        user: UserProfile, source_user: UserProfile, record: "EncrypedRecord"
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user,
            source_user,
            str(record.id),
            record.record_token,
            NotificationGroupType.RECORD,
            NotificationType.RECORD__RECORD_MESSAGE_ADDED,
        )

    @staticmethod
    def create_notification_new_record(
        user: UserProfile, source_user: UserProfile, record: "EncryptedRecord"
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(record.id),
            ref_text=record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__CREATED,
        )

    @staticmethod
    def create_notification_updated_record(
        user: UserProfile,
        source_user: UserProfile,
        record: "EncryptedRecord",
        text: str,
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(record.id),
            ref_text=record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__UPDATED,
            text=text,
        )

    @staticmethod
    def create_notification_added_to_group(
        user: UserProfile, source_user: UserProfile, group: "Group"
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(group.id),
            ref_text=group.name,
            notification_group_type=NotificationGroupType.GROUP,
            notification_type=NotificationType.GROUP__ADDED_ME,
        )

    @staticmethod
    def create_notification_removed_from_group(
        user: UserProfile, source_user: UserProfile, group: "Group"
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(group.id),
            ref_text=group.name,
            notification_group_type=NotificationGroupType.GROUP,
            notification_type=NotificationType.GROUP__REMOVED_ME,
        )

    @staticmethod
    def create_notification_record_document_added(
        user: UserProfile,
        source_user: UserProfile,
        record: "EncryptedRecord",
        text: str,
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(record.id),
            ref_text=record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__RECORD_DOCUMENT_ADDED,
            text=text,
        )

    @staticmethod
    def create_notification_record_document_modified(
        user: UserProfile,
        source_user: UserProfile,
        record: "EncryptedRecord",
        text: str,
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(record.id),
            ref_text=record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__RECORD_DOCUMENT_MODIFIED,
            text=text,
        )

    @staticmethod
    def create_notification_record_deletion_request_requested(
        user: UserProfile, source_user: UserProfile, record: "EncryptedRecord"
    ) -> (NotificationGroup, "Notification"):
        return Notification.objects.create_notification(
            user=user,
            source_user=source_user,
            ref_id=str(record.id),
            ref_text=record.record_token,
            notification_group_type=NotificationGroupType.RECORD_DELETION_REQUEST,
            notification_type=NotificationType.RECORD_DELETION_REQUEST__REQUESTED,
        )

    @staticmethod
    def notify_record_permission_accepted(
        source_user: UserProfile, record_permission: "EncryptedRecordPermission"
    ):
        notification_users: [
            UserProfile
        ] = record_permission.record.get_notification_users()
        for user in notification_users:
            if user != source_user and user != record_permission.request_from:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_permission.record.id),
                    ref_text=record_permission.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__NEW_RECORD_PERMISSION,
                )

        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_permission.record.id),
                    ref_text=record_permission.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD_PERMISSION_REQUEST,
                    notification_type=NotificationType.RECORD_PERMISSION_REQUEST__ACCEPTED,
                )

        Notification.objects.create_notification(
            user=record_permission.request_from,
            source_user=source_user,
            ref_id=str(record_permission.record.id),
            ref_text=record_permission.record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__ACCESS_GRANTED,
        )

    @staticmethod
    def notify_record_permission_declined(
        source_user: UserProfile, record_permission: "EncryptedRecordPermission"
    ):
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_permission.record.id),
                    ref_text=record_permission.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD_PERMISSION_REQUEST,
                    notification_type=NotificationType.RECORD_PERMISSION_REQUEST__DECLINED,
                )

        Notification.objects.create_notification(
            user=record_permission.request_from,
            source_user=source_user,
            ref_id=str(record_permission.record.id),
            ref_text=record_permission.record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__ACCESS_DENIED,
        )

    @staticmethod
    def notify_record_deletion_requested(
        source_user: UserProfile, record_deletion: "EncryptedRecordDeletionRequest"
    ):
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_deletion.record.id),
                    ref_text=record_deletion.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD_DELETION_REQUEST,
                    notification_type=NotificationType.RECORD_DELETION_REQUEST__REQUESTED,
                )

    @staticmethod
    def notify_record_permission_requested(
        source_user: UserProfile, record_permission: "EncryptedRecordPermission"
    ):
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_permission.record.id),
                    ref_text=record_permission.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD_PERMISSION_REQUEST,
                    notification_type=NotificationType.RECORD_PERMISSION_REQUEST__REQUESTED,
                )


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

    objects = NotificationManager()

    def __str__(self):
        return "notification: " + str(self.id)

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
