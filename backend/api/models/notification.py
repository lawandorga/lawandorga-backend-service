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
    def notify_record_permission_accepted(
        source_user: UserProfile, record_permission: "EncryptedRecordPermission"
    ):
        """
        creates notification for accepted record permission request

        creates notifications for every user with permit record permission in rlc
        creates notifications for every user with access to record (working_on or record permission)
        except source_user and record permission requestor
        creates notification for requestor that record permission is accepted

        :param source_user:
        :param record_permission:
        :return:
        """
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
            if user != source_user and user != record_permission.request_from:
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
        """
        created notification for new deletion request

        creates notifications for every user with process record deletion request
        except source_user
        :param source_user:
        :param record_deletion:
        :return:
        """
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
        """
        creates notification for new record permission request

        creates  notifications for every user with permit record permission in rlc
        except source_user
        :param source_user:
        :param record_permission:
        :return:
        """
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

    @staticmethod
    def notify_record_deletion_accepted(
        source_user: UserProfile, record_deletion: "EncryptedRecordDeletionRequest"
    ):
        """
        creates notification for a accepted record deletion

        creates notifications for every user with process record deletion request
        creates notifications for every user with access to record (working_on and record_permission)
        except source_user
        :param source_user:
        :param record_deletion:
        :return:
        """
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
                    notification_type=NotificationType.RECORD_DELETION_REQUEST__ACCEPTED,
                )

        notification_users: [
            UserProfile
        ] = record_deletion.record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_deletion.record.id),
                    ref_text=record_deletion.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__DELETED,
                )

    @staticmethod
    def notify_record_deletion_declined(
        source_user: UserProfile, record_deletion: "EncryptedRecordDeletionRequest"
    ):
        """
        created notifications for declined record deletion

        creates notifications for every user with process record deletion request in rlc
        except source user

        creates notification for requestor of record deletion
        :param source_user:
        :param record_deletion:
        :return:
        """
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
                    notification_type=NotificationType.RECORD_DELETION_REQUEST__DECLINED,
                )

        Notification.objects.create_notification(
            user=record_deletion.request_from,
            source_user=source_user,
            ref_id=str(record_deletion.record.id),
            ref_text=record_deletion.record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__DELETION_REQUEST_DENIED,
        )

    @staticmethod
    def notify_group_member_added(
        source_user: UserProfile, new_user: UserProfile, group: "Group"
    ):
        """
        creates notifications after user is added to group

        only adds one notification for new user
        :param source_user:
        :param new_user:
        :param group:
        :return:
        """
        Notification.objects.create_notification(
            user=new_user,
            source_user=source_user,
            ref_id=str(group.id),
            ref_text=group.name,
            notification_group_type=NotificationGroupType.GROUP,
            notification_type=NotificationType.GROUP__ADDED_ME,
        )

    @staticmethod
    def notify_group_member_removed(
        source_user: UserProfile, new_user: UserProfile, group: "Group"
    ):
        """
        creates notifications after user removed from group

        only adds one notification for removed user
        :param source_user:
        :param new_user:
        :param group:
        :return:
        """
        Notification.objects.create_notification(
            user=new_user,
            source_user=source_user,
            ref_id=str(group.id),
            ref_text=group.name,
            notification_group_type=NotificationGroupType.GROUP,
            notification_type=NotificationType.GROUP__REMOVED_ME,
        )

    @staticmethod
    def notify_record_patched(
        source_user: UserProfile, record: "EncryptedRecord", text: str
    ):
        """
        creates notification if record was patched

        creates notification for all users with access to record
        except source_user
        :param source_user:
        :param record:
        :param text:
        :return:
        """
        notification_users: [UserProfile] = record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record.id),
                    ref_text=record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__UPDATED,
                    text=text,
                )

    @staticmethod
    def notify_record_message_added(
        source_user: UserProfile, record_message: "EncryptedRecordMessage"
    ):
        """
        creates notification after record message was added to record

        creates notification for all users with access to record
        except source_user
        :param source_user:
        :param record_message:
        :return:
        """
        notification_users: [
            UserProfile
        ] = record_message.record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_message.record.id),
                    ref_text=record_message.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__RECORD_MESSAGE_ADDED,
                )

    @staticmethod
    def notify_record_document_added(
        source_user: UserProfile, record_document: "EncryptedRecordDocument"
    ):
        """
        creates notifications after record document was added to record

        creates notifications for all users which have access to record
        except source_user
        :param source_user:
        :param record_document:
        :return:
        """
        notification_users: [
            UserProfile
        ] = record_document.record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_document.record.id),
                    ref_text=record_document.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__RECORD_DOCUMENT_ADDED,
                )

    @staticmethod
    def notify_record_document_modified(
        source_user: UserProfile, record_document: "EncryptedRecordDocument"
    ):
        """
        creates notifications after record document was modified (reuploaded)

        creates notifications for all users which have access to record
        except source_user
        :param source_user:
        :param record_document:
        :return:
        """
        notification_users: [
            UserProfile
        ] = record_document.record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record_document.record.id),
                    ref_text=record_document.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__RECORD_DOCUMENT_MODIFIED,
                )

    @staticmethod
    def notify_record_created(source_user: UserProfile, record: "EncryptedRecord"):
        """
        creates notifications after record was created

        creates notifications for all users which have access to record
        except source_user
        :param source_user:
        :param record:
        :return:
        """
        notification_users: [UserProfile] = record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(record.id),
                    ref_text=record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__CREATED,
                )

    from backend.api.models import NewUserRequest

    @staticmethod
    def notify_new_user_request(
        source_user: UserProfile, new_user_request: NewUserRequest
    ):
        """
        creates notifications after new user request (registering in rlc)

        creates notifications for all users which have accept new users permission
        (source user is not possible)
        :param source_user:
        :param new_user_request:
        :return:
        """
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_ACCEPT_NEW_USERS_RLC],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            Notification.objects.create_notification(
                user=user,
                source_user=source_user,
                ref_id=str(new_user_request.request_from.id),
                ref_text=new_user_request.request_from.name,
                notification_group_type=NotificationGroupType.USER_REQUEST,
                notification_type=NotificationType.USER_REQUEST__REQUESTED,
            )

    @staticmethod
    def notify_new_user_accepted(
        source_user: UserProfile, new_user_request: NewUserRequest
    ):
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_ACCEPT_NEW_USERS_RLC],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(new_user_request.request_from.id),
                    ref_text=new_user_request.request_from.name,
                    notification_group_type=NotificationGroupType.USER_REQUEST,
                    notification_type=NotificationType.USER_REQUEST__ACCEPTED,
                )

    @staticmethod
    def notify_new_user_declined(
        source_user: UserProfile, new_user_request: NewUserRequest
    ):
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[permissions.PERMISSION_ACCEPT_NEW_USERS_RLC],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(new_user_request.request_from.id),
                    ref_text=new_user_request.request_from.name,
                    notification_group_type=NotificationGroupType.USER_REQUEST,
                    notification_type=NotificationType.USER_REQUEST__DECLINED,
                )

    @staticmethod
    def notify_new_record_document_deletion_request(
        source_user: UserProfile,
        document_deletion_request: "EncryptedRecordDocumentDeletionRequest",
    ):
        """
        creates notification for requested record document deletion

        creates notification for every user with process record document deletion request
        except source user
        :param source_user:
        :param document_deletion_request:
        :return:
        """
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[
                permissions.PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS
            ],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(document_deletion_request.document.id),
                    ref_text=document_deletion_request.document.name,
                    notification_group_type=NotificationGroupType.RECORD_DOCUMENT_DELETION_REQUEST,
                    notification_type=NotificationType.RECORD_DOCUMENT_DELETION_REQUEST__REQUESTED,
                )

    @staticmethod
    def notify_record_document_deletion_accepted(
        source_user: UserProfile,
        document_deletion_request: "EncryptedRecordDocumentDeletionRequest",
    ):
        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[
                permissions.PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS
            ],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(document_deletion_request.document.id),
                    ref_text=document_deletion_request.document.name,
                    notification_group_type=NotificationGroupType.RECORD_DOCUMENT_DELETION_REQUEST,
                    notification_type=NotificationType.RECORD_DOCUMENT_DELETION_REQUEST__ACCEPTED,
                )

        notification_users: [
            UserProfile
        ] = document_deletion_request.document.record.get_notification_users()
        for user in notification_users:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(document_deletion_request.document.record.id),
                    ref_text=document_deletion_request.document.record.record_token,
                    notification_group_type=NotificationGroupType.RECORD,
                    notification_type=NotificationType.RECORD__DOCUMENT_DELETED,
                    text=document_deletion_request.document.name,
                )

    @staticmethod
    def notify_record_document_deletion_declined(
        source_user: UserProfile,
        document_deletion_request: "EncryptedRecordDocumentDeletionRequest",
    ):
        Notification.objects.create_notification(
            user=document_deletion_request.request_from,
            source_user=source_user,
            ref_id=str(document_deletion_request.document.record.id),
            ref_text=document_deletion_request.document.record.record_token,
            notification_group_type=NotificationGroupType.RECORD,
            notification_type=NotificationType.RECORD__DOCUMENT_DELETION_REQUEST_DECLINED,
        )

        users_with_permissions: [
            UserProfile
        ] = UserProfile.objects.get_users_with_special_permissions(
            permissions=[
                permissions.PERMISSION_PROCESS_RECORD_DOCUMENT_DELETION_REQUESTS
            ],
            from_rlc=source_user.rlc,
            for_rlc=source_user.rlc,
        )
        for user in users_with_permissions:
            if user != source_user:
                Notification.objects.create_notification(
                    user=user,
                    source_user=source_user,
                    ref_id=str(document_deletion_request.document.id),
                    ref_text=document_deletion_request.document.name,
                    notification_group_type=NotificationGroupType.RECORD_DOCUMENT_DELETION_REQUEST,
                    notification_type=NotificationType.RECORD_DOCUMENT_DELETION_REQUEST__DECLINED,
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
