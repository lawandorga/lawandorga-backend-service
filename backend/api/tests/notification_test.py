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

from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api.models import *
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static import permissions


class NotificationTest(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        self.base_record_fixtures = CreateFixtures.create_record_base_fixtures(
            self.base_fixtures["rlc"],
            [
                self.base_fixtures["users"][0]["user"],
                self.base_fixtures["users"][1]["user"],
                self.base_fixtures["users"][2]["user"],
            ],
        )
        self.users = [
            self.base_fixtures["users"][0]["user"],
            self.base_fixtures["users"][1]["user"],
            self.base_fixtures["users"][2]["user"],
        ]
        self.record: record_models.EncryptedRecord = self.base_record_fixtures[
            "records"
        ][0]["record"]
        self.group: Group = self.base_fixtures["groups"][0]

    def test_create_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())
        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification(
            self.users[0],
            self.users[1],
            "666",
            "name",
            NotificationGroupType.RECORD,
            NotificationType.RECORD__CREATED,
        )
        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())

        group_from_db_first: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db_first)
        self.assertEqual(self.users[0], group_from_db_first.user)
        self.assertEqual(1, group_from_db_first.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group_from_db_first.type)
        self.assertEqual("666", group_from_db_first.ref_id)
        self.assertEqual("name", group_from_db_first.ref_text)

        first_notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, first_notification_from_db)
        self.assertEqual(
            group_from_db_first, first_notification_from_db.notification_group
        )
        self.assertEqual(self.users[1], first_notification_from_db.source_user)
        self.assertEqual(
            NotificationType.RECORD__CREATED.value, first_notification_from_db.type
        )

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification(
            self.users[0],
            self.users[1],
            "666",
            "name",
            NotificationGroupType.RECORD,
            NotificationType.RECORD__UPDATED,
        )
        self.assertEqual(1, NotificationGroup.objects.count())
        self.assertEqual(2, Notification.objects.count())

        group_from_db_second: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db_second)
        self.assertEqual(2, group_from_db_second.notifications.count())
        self.assertTrue(
            group_from_db_second.last_activity > group_from_db_first.last_activity
        )

        second_notification_from_db: Notification = group_from_db_second.notifications.filter(
            ~Q(id=first_notification_from_db.id)
        ).first()
        self.assertEqual(self.users[1], second_notification_from_db.source_user)
        self.assertEqual(
            NotificationType.RECORD__UPDATED.value, second_notification_from_db.type
        )

    def test_read_notification(self):
        user: UserProfile = self.base_fixtures["users"][0]["user"]
        client: APIClient = self.base_fixtures["users"][0]["client"]
        notification_groups: [
            NotificationGroup
        ] = CreateFixtures.add_notification_fixtures(
            main_user=user,
            source_user=self.base_fixtures["users"][1]["user"],
            records=[
                self.base_record_fixtures["records"][0]["record"],
                self.base_record_fixtures["records"][1]["record"],
            ],
            groups=[self.base_fixtures["groups"][0], self.base_fixtures["groups"][1]],
        )

        notifications: [Notification] = notification_groups[0].notifications.all()
        response: Response = client.patch(
            "/api/notifications/" + str(notifications[0].id) + "/",
            {"read": True},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        notification: Notification = Notification.objects.get(pk=notifications[0].id)
        self.assertTrue(notification.read)
        notification_group: NotificationGroup = NotificationGroup.objects.get(
            pk=notification_groups[0].id
        )
        self.assertFalse(notification_group.read)
        self.assertTrue(
            notification_groups[0].last_activity == notification_group.last_activity
        )

        response: Response = client.patch(
            "/api/notifications/" + str(notifications[2].id) + "/",
            {"read": True},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        notification: Notification = Notification.objects.get(pk=notifications[2].id)
        self.assertTrue(notification.read)
        notification_group: NotificationGroup = NotificationGroup.objects.get(
            pk=notification_groups[0].id
        )
        self.assertTrue(
            notification_groups[0].last_activity == notification_group.last_activity
        )
        self.assertTrue(notification_group.read)

        response: Response = client.patch(
            "/api/notifications/" + str(notifications[2].id) + "/",
            {"read": False},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        notification: Notification = Notification.objects.get(pk=notifications[2].id)
        self.assertFalse(notification.read)
        notification_group: NotificationGroup = NotificationGroup.objects.get(
            pk=notification_groups[0].id
        )
        self.assertFalse(notification_group.read)
        self.assertTrue(
            notification_groups[0].last_activity == notification_group.last_activity
        )

    def test_create_new_user_request_notification(self):
        pass  # TODO: just for other admins

    def test_request_record_permission_notifications(self):
        """
        check if notifications are created accordingly
        X for each user with process permission
        :return:
        """
        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()
        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_VIEW_RECORDS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][2],
        )
        has_permission.save()

        url = (
            "/api/records/record/"
            + str(self.base_record_fixtures["records"][0]["record"].id)
            + "/request_permission"
        )
        notification_groups_before: int = NotificationGroup.objects.count()
        notifications_before: int = Notification.objects.count()

        response: Response = self.base_fixtures["users"][3]["client"].post(url, {})
        self.assertEqual(200, response.status_code)

        self.assertEqual(
            notification_groups_before + 2, NotificationGroup.objects.count()
        )
        self.assertEqual(notifications_before + 2, Notification.objects.count())

        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD_PERMISSION_REQUEST__REQUESTED.value
            ).count(),
        )

    def test_accept_record_permission_notifications(self):
        """
        check if notifications are generated accordingly
        1 for requesting user
        X for every user with process permission
        Y for every user with access to record (working on or record permission)

        in this case 4 in total: 1 requesting, 1 process, 2 record
        :return:
        """
        process_client: APIClient = self.base_fixtures["users"][0]["client"]
        process_private: bytes = self.base_fixtures["users"][0]["private"]

        request_user: UserProfile = self.base_fixtures["users"][3]["user"]

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        record_permission: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission(
            request_from=request_user,
            record=self.base_record_fixtures["records"][0]["record"],
            state="re",
        )
        record_permission.save()

        response: Response = process_client.post(
            "/api/records/e_record_permission_requests/",
            {"id": record_permission.id, "action": "accept"},
            format="json",
            **{"HTTP_PRIVATE_KEY": process_private},
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(4, NotificationGroup.objects.count())
        self.assertEqual(4, Notification.objects.count())

        self.assertEqual(
            1, NotificationGroup.objects.filter(user=request_user).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=request_user
        ).first()
        self.assertEqual(1, group.notifications.count())
        self.assertEqual(
            NotificationGroupType.RECORD.value, group.type,
        )
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD__ACCESS_GRANTED.value, notification.type,
        )

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][2]["user"]
            ).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=self.base_fixtures["users"][2]["user"]
        ).first()
        self.assertEqual(1, group.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group.type)
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD__NEW_RECORD_PERMISSION.value, notification.type
        )

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][1]["user"],
                type=NotificationGroupType.RECORD.value,
            ).count(),
        )
        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][1]["user"],
                type=NotificationGroupType.RECORD_PERMISSION_REQUEST.value,
            ).count(),
        )

    def test_decline_record_permission_notifications(self):
        """
        check if notifications are generated accordingly
        1 for requesting user, X for every user with process permission
        in this case in total 2
        :return:
        """
        process_client: APIClient = self.base_fixtures["users"][0]["client"]
        process_private: bytes = self.base_fixtures["users"][0]["private"]

        request_user: UserProfile = self.base_fixtures["users"][3]["user"]

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        record_permission: record_models.EncryptedRecordPermission = record_models.EncryptedRecordPermission(
            request_from=request_user,
            record=self.base_record_fixtures["records"][0]["record"],
            state="re",
        )
        record_permission.save()

        response: Response = process_client.post(
            "/api/records/e_record_permission_requests/",
            {"id": record_permission.id, "action": "decline"},
            format="json",
            **{"HTTP_PRIVATE_KEY": process_private},
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, NotificationGroup.objects.count())
        self.assertEqual(2, Notification.objects.count())

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=record_permission.request_from
            ).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=record_permission.request_from
        ).first()
        self.assertEqual(NotificationGroupType.RECORD.value, group.type)
        self.assertEqual(1, group.notifications.count())
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD__ACCESS_DENIED.value, notification.type
        )

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][1]["user"]
            ).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=self.base_fixtures["users"][1]["user"]
        ).first()
        self.assertEqual(
            NotificationGroupType.RECORD_PERMISSION_REQUEST.value, group.type
        )
        self.assertEqual(1, group.notifications.count())
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD_PERMISSION_REQUEST__DECLINED.value,
            notification.type,
        )

    def test_notify_record_permission_accepted(self):
        request_user: UserProfile = self.base_fixtures["users"][3]["user"]
        process_user: UserProfile = self.base_fixtures["users"][0]["user"]
        record_permission: (
            record_models.EncryptedRecordPermission
        ) = record_models.EncryptedRecordPermission(
            request_from=request_user,
            state="ac",
            request_processed=process_user,
            record=self.record,
        )

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_record_permission_accepted(
            process_user, record_permission
        )

        self.assertEqual(4, NotificationGroup.objects.count())
        self.assertEqual(4, Notification.objects.count())

        self.assertEqual(
            1, NotificationGroup.objects.filter(user=request_user).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=request_user
        ).first()
        self.assertEqual(1, group.notifications.count())
        self.assertEqual(
            NotificationGroupType.RECORD.value, group.type,
        )
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD__ACCESS_GRANTED.value, notification.type,
        )

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][2]["user"]
            ).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=self.base_fixtures["users"][2]["user"]
        ).first()
        self.assertEqual(1, group.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group.type)
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD__NEW_RECORD_PERMISSION.value, notification.type
        )

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][1]["user"],
                type=NotificationGroupType.RECORD.value,
            ).count(),
        )
        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][1]["user"],
                type=NotificationGroupType.RECORD_PERMISSION_REQUEST.value,
            ).count(),
        )

    def test_notify_record_permission_declined(self):
        request_user: UserProfile = self.base_fixtures["users"][3]["user"]
        process_user: UserProfile = self.base_fixtures["users"][0]["user"]
        record_permission: (
            record_models.EncryptedRecordPermission
        ) = record_models.EncryptedRecordPermission(
            request_from=request_user,
            state="de",
            request_processed=process_user,
            record=self.record,
        )

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_record_permission_declined(
            process_user, record_permission
        )

        self.assertEqual(2, NotificationGroup.objects.count())
        self.assertEqual(2, Notification.objects.count())

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=record_permission.request_from
            ).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=record_permission.request_from
        ).first()
        self.assertEqual(NotificationGroupType.RECORD.value, group.type)
        self.assertEqual(1, group.notifications.count())
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD__ACCESS_DENIED.value, notification.type
        )

        self.assertEqual(
            1,
            NotificationGroup.objects.filter(
                user=self.base_fixtures["users"][1]["user"]
            ).count(),
        )
        group: NotificationGroup = NotificationGroup.objects.filter(
            user=self.base_fixtures["users"][1]["user"]
        ).first()
        self.assertEqual(
            NotificationGroupType.RECORD_PERMISSION_REQUEST.value, group.type
        )
        self.assertEqual(1, group.notifications.count())
        notification: Notification = group.notifications.first()
        self.assertEqual(
            NotificationType.RECORD_PERMISSION_REQUEST__DECLINED.value,
            notification.type,
        )

    def test_notify_record_permission_requested(self):
        request_user: UserProfile = self.base_fixtures["users"][3]["user"]
        record_permission: (
            record_models.EncryptedRecordPermission
        ) = record_models.EncryptedRecordPermission(
            request_from=request_user, state="re", record=self.record,
        )

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PERMIT_RECORD_PERMISSION_REQUESTS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_record_permission_requested(
            source_user=request_user, record_permission=record_permission
        )

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD_PERMISSION_REQUEST__REQUESTED.value
            ).count(),
        )

    def test_notify_record_deletion_requested(self):
        request_user: UserProfile = self.base_fixtures["users"][3]["user"]
        record_deletion: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest(
            request_from=request_user, state="re", record=self.record,
        )

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_record_deletion_requested(
            request_user, record_deletion
        )

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD_DELETION_REQUEST__REQUESTED.value
            ).count(),
        )

    def test_notify_record_deletion_accepted(self):
        request_user: UserProfile = self.base_fixtures["users"][2]["user"]
        process_user: UserProfile = self.base_fixtures["users"][0]["user"]
        record_deletion: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest(
            request_from=request_user,
            state="ac",
            record=self.record,
            request_processed=process_user,
        )

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_record_deletion_accepted(
            process_user, record_deletion
        )

        self.assertEqual(3, Notification.objects.count())
        self.assertEqual(3, NotificationGroup.objects.count())

        self.assertEqual(
            1,
            Notification.objects.filter(
                type=NotificationType.RECORD_DELETION_REQUEST__ACCEPTED.value
            ).count(),
        )
        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD__DELETED.value
            ).count(),
        )

    def test_notify_record_deletion_declined(self):
        request_user: UserProfile = self.base_fixtures["users"][2]["user"]
        process_user: UserProfile = self.base_fixtures["users"][0]["user"]
        record_deletion: (
            record_models.EncryptedRecordDeletionRequest
        ) = record_models.EncryptedRecordDeletionRequest(
            request_from=request_user,
            state="de",
            record=self.record,
            request_processed=process_user,
        )

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_PROCESS_RECORD_DELETION_REQUESTS
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_record_deletion_declined(
            process_user, record_deletion
        )

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

        self.assertEqual(
            1,
            Notification.objects.filter(
                type=NotificationType.RECORD_DELETION_REQUEST__DECLINED.value
            ).count(),
        )
        self.assertEqual(
            1,
            Notification.objects.filter(
                type=NotificationType.RECORD__DELETION_REQUEST_DENIED.value
            ).count(),
        )

    def test_notify_group_member_added(self):
        Notification.objects.notify_group_member_added(
            self.users[0], self.users[1], self.group
        )

        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())
        self.assertEqual(self.group.name, NotificationGroup.objects.first().ref_text)
        self.assertEqual(
            NotificationType.GROUP__ADDED_ME.value, Notification.objects.first().type
        )

    def test_notify_group_member_removed(self):
        Notification.objects.notify_group_member_removed(
            self.users[0], self.users[1], self.group
        )

        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())
        self.assertEqual(self.group.name, NotificationGroup.objects.first().ref_text)
        self.assertEqual(
            NotificationType.GROUP__REMOVED_ME.value, Notification.objects.first().type
        )

    def test_notify_record_created(self):
        Notification.objects.notify_record_created(
            self.base_fixtures["users"][3]["user"], self.record
        )

        self.assertEqual(3, Notification.objects.count())
        self.assertEqual(3, NotificationGroup.objects.count())

        self.assertEqual(
            3,
            Notification.objects.filter(
                type=NotificationType.RECORD__CREATED.value
            ).count(),
        )
        self.assertEqual(
            1,
            Notification.objects.filter(notification_group__user=self.users[0]).count(),
        )
        Notification.objects.all().delete()
        NotificationGroup.objects.all().delete()

        Notification.objects.notify_record_created(self.users[0], self.record)
        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

    def test_notify_record_patched(self):
        text = "circumstances,contact_information"
        Notification.objects.notify_record_patched(
            self.users[0], self.record, text=text
        )
        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD__UPDATED.value
            ).count(),
        )
        notification_from_db: Notification = Notification.objects.filter(
            notification_group__user=self.users[1]
        ).first()
        self.assertEqual("circumstances,contact_information", notification_from_db.text)

    def test_notify_record_message_added(self):
        message = record_models.EncryptedRecordMessage(
            sender=self.users[0], record=self.record, message=b"test"
        )
        message.save()

        Notification.objects.notify_record_message_added(self.users[0], message)

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD__RECORD_MESSAGE_ADDED.value
            ).count(),
        )

    def test_notify_record_document_added(self):
        document = record_models.EncryptedRecordDocument(
            name="test doc", creator=self.users[0], record=self.record, file_size=12321,
        )
        document.save()

        Notification.objects.notify_record_document_added(self.users[0], document)

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD__RECORD_DOCUMENT_ADDED.value
            ).count(),
        )

    def test_notify_record_document_modified(self):
        document = record_models.EncryptedRecordDocument(
            name="test doc", creator=self.users[0], record=self.record, file_size=12321,
        )
        document.save()

        Notification.objects.notify_record_document_modified(self.users[0], document)

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.RECORD__RECORD_DOCUMENT_MODIFIED.value
            ).count(),
        )

    def test_notify_new_user_request(self):
        new_user: UserProfile = UserProfile(
            is_active=False,
            is_superuser=False,
            email="newuser@law-orga.de",
            name="new user",
            rlc=self.base_fixtures["rlc"],
        )
        new_user.save()
        request = NewUserRequest(request_from=new_user)
        request.save()

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_ACCEPT_NEW_USERS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_new_user_request(new_user, request)

        self.assertEqual(2, Notification.objects.count())
        self.assertEqual(2, NotificationGroup.objects.count())

        self.assertEqual(
            2,
            Notification.objects.filter(
                type=NotificationType.USER_REQUEST__REQUESTED.value
            ).count(),
        )

    def test_notify_new_user_accepted(self):
        new_user: UserProfile = UserProfile(
            is_active=False,
            is_superuser=False,
            email="newuser@law-orga.de",
            name="new user",
            rlc=self.base_fixtures["rlc"],
        )
        new_user.save()
        request = NewUserRequest(request_from=new_user, state="ac")
        request.save()

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_ACCEPT_NEW_USERS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_new_user_accepted(
            self.base_fixtures["users"][0]["user"], request
        )

        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())

        self.assertEqual(
            1,
            Notification.objects.filter(
                type=NotificationType.USER_REQUEST__ACCEPTED.value
            ).count(),
        )

    def test_notify_new_user_declined(self):
        new_user: UserProfile = UserProfile(
            is_active=False,
            is_superuser=False,
            email="newuser@law-orga.de",
            name="new user",
            rlc=self.base_fixtures["rlc"],
        )
        new_user.save()
        request = NewUserRequest(request_from=new_user, state="de")
        request.save()

        permission: Permission = Permission.objects.get(
            name=permissions.PERMISSION_ACCEPT_NEW_USERS_RLC
        )
        has_permission: HasPermission = HasPermission(
            permission=permission,
            permission_for_rlc=self.base_fixtures["rlc"],
            group_has_permission=self.base_fixtures["groups"][0],
        )
        has_permission.save()

        Notification.objects.notify_new_user_declined(
            self.base_fixtures["users"][0]["user"], request
        )

        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())

        self.assertEqual(
            1,
            Notification.objects.filter(
                type=NotificationType.USER_REQUEST__DECLINED.value
            ).count(),
        )
