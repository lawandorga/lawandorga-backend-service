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
from backend.static.queryset_difference import QuerysetDifference


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

    def test_create_new_record_message_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_new_record_message(
            self.users[0], self.users[1], self.record
        )
        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())

        group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db)
        self.assertEqual(self.users[0], group_from_db.user)
        self.assertEqual(1, group_from_db.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group_from_db.type)
        self.assertEqual(str(self.record.id), group_from_db.ref_id)
        self.assertEqual(self.record.record_token, group_from_db.ref_text)

        notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, notification_from_db)
        self.assertEqual(group_from_db, notification_from_db.notification_group)
        self.assertEqual(self.users[1], notification_from_db.source_user)
        self.assertEqual(
            NotificationType.RECORD__RECORD_MESSAGE_ADDED.value,
            notification_from_db.type,
        )

    def test_create_new_record_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_new_record(
            self.users[0], self.users[1], self.record
        )
        self.assertEqual(1, Notification.objects.count())
        self.assertEqual(1, NotificationGroup.objects.count())

        group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db)
        self.assertEqual(self.users[0], group_from_db.user)
        self.assertEqual(1, group_from_db.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group_from_db.type)
        self.assertEqual(str(self.record.id), group_from_db.ref_id)
        self.assertEqual(self.record.record_token, group_from_db.ref_text)

        notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, notification_from_db)
        self.assertEqual(group_from_db, notification_from_db.notification_group)
        self.assertEqual(self.users[1], notification_from_db.source_user)
        self.assertEqual(
            NotificationType.RECORD__CREATED.value, notification_from_db.type
        )

    def test_create_record_update_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())

        notification_text = "circumstances,record_note"
        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_updated_record(
            user=self.users[0],
            source_user=self.users[1],
            record=self.record,
            text=notification_text,
        )

        group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db)
        self.assertEqual(self.users[0], group_from_db.user)
        self.assertEqual(1, group_from_db.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group_from_db.type)
        self.assertEqual(str(self.record.id), group_from_db.ref_id)
        self.assertEqual(self.record.record_token, group_from_db.ref_text)

        notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, notification_from_db)
        self.assertEqual(group_from_db, notification_from_db.notification_group)
        self.assertEqual(self.users[1], notification_from_db.source_user)
        self.assertEqual(
            NotificationType.RECORD__UPDATED.value, notification_from_db.type
        )
        self.assertEqual(notification_text, notification_from_db.text)

    def test_create_added_removed_group_notifications(self):
        self.assertEqual(0, NotificationGroup.objects.count())
        self.assertEqual(0, Notification.objects.count())

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_added_to_group(
            user=self.users[0], source_user=self.users[1], group=self.group
        )

        self.assertEqual(1, NotificationGroup.objects.count())
        self.assertEqual(1, Notification.objects.count())

        first_group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, first_group_from_db)
        self.assertEqual(self.users[0], first_group_from_db.user)
        self.assertEqual(1, first_group_from_db.notifications.count())
        self.assertEqual(NotificationGroupType.GROUP.value, first_group_from_db.type)
        self.assertEqual(str(self.group.id), first_group_from_db.ref_id)
        self.assertEqual(self.group.name, first_group_from_db.ref_text)

        first_notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, first_notification_from_db)
        self.assertEqual(
            first_group_from_db, first_notification_from_db.notification_group
        )
        self.assertEqual(self.users[1], first_notification_from_db.source_user)
        self.assertEqual(
            NotificationType.GROUP__ADDED_ME.value, first_notification_from_db.type
        )

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_removed_from_group(
            user=self.users[0], source_user=self.users[1], group=self.group
        )
        self.assertEqual(1, NotificationGroup.objects.count())
        self.assertEqual(2, Notification.objects.count())

        second_group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, second_group_from_db)
        self.assertEqual(2, second_group_from_db.notifications.count())
        self.assertTrue(
            second_group_from_db.last_activity > first_group_from_db.last_activity
        )

        second_notification_from_db: Notification = second_group_from_db.notifications.filter(
            ~Q(id=first_notification_from_db.id)
        ).first()
        self.assertEqual(return_notification, second_notification_from_db)
        self.assertEqual(self.users[1], second_notification_from_db.source_user)
        self.assertEqual(
            NotificationType.GROUP__REMOVED_ME.value, second_notification_from_db.type
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

        notifications: Notification = notification_groups[0].notifications.all()
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
            "/api/notifications/" + str(notifications[1].id) + "/",
            {"read": True},
            format="json",
        )
        self.assertEqual(200, response.status_code)
        notification: Notification = Notification.objects.get(pk=notifications[1].id)
        self.assertTrue(notification.read)
        notification_group: NotificationGroup = NotificationGroup.objects.get(
            pk=notification_groups[0].id
        )
        self.assertTrue(
            notification_groups[0].last_activity == notification_group.last_activity
        )
        self.assertFalse(notification_group.read)

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

    def test_create_new_record_document_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_record_document_added(
            user=self.users[0], source_user=self.users[1], record=self.record
        )

        group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db)
        self.assertEqual(self.users[0], group_from_db.user)
        self.assertEqual(1, group_from_db.notifications.count())
        self.assertEqual(NotificationGroupType.RECORD.value, group_from_db.type)
        self.assertEqual(str(self.record.id), group_from_db.ref_id)
        self.assertEqual(self.record.record_token, group_from_db.ref_text)

        notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, notification_from_db)
        self.assertEqual(group_from_db, notification_from_db.notification_group)
        self.assertEqual(self.users[1], notification_from_db.source_user)
        self.assertEqual(
            NotificationType.RECORD__RECORD_DOCUMENT_ADDED.value,
            notification_from_db.type,
        )

    def test_create_new_record_document_modified_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_record_document_modified(
            user=self.users[0], source_user=self.users[1], record=self.record
        )

        group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db)
        self.assertEqual(NotificationGroupType.RECORD.value, group_from_db.type)

        notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, notification_from_db)
        self.assertEqual(
            NotificationType.RECORD__RECORD_DOCUMENT_MODIFIED.value,
            notification_from_db.type,
        )

    def test_create_record_permission_request_notification(self):
        self.assertEqual(0, Notification.objects.count())
        self.assertEqual(0, NotificationGroup.objects.count())

        (
            return_notification_group,
            return_notification,
        ) = Notification.objects.create_notification_record_permission_request_requested(
            user=self.users[0], source_user=self.users[1], record=self.record
        )

        group_from_db: NotificationGroup = NotificationGroup.objects.first()
        self.assertEqual(return_notification_group, group_from_db)
        self.assertEqual(
            NotificationGroupType.RECORD_PERMISSION_REQUEST.value, group_from_db.type
        )

        notification_from_db: Notification = Notification.objects.first()
        self.assertEqual(return_notification, notification_from_db)
        self.assertEqual(
            NotificationType.RECORD_PERMISSION_REQUEST__REQUESTED.value,
            notification_from_db.type,
        )
        # TODO: requested and processed (-> for requesting user and other admins)

    def test_create_record_deletion_request_notification(self):
        pass  # TODO: requested and processsed (-> for requesting user and other adminsa)

    def test_create_new_user_request_notification(self):
        pass  # TODO: just for ohter admins

    def test_accept_record_permission_notifications(self):
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
