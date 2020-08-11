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


from django.db.models import Q
from django.test import TransactionTestCase
from rest_framework.response import Response
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models
from backend.static.notification_enums import NotificationType


class NotificationGroupTest(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [self.base_fixtures['users'][0]['user'],
                                           self.base_fixtures['users'][1]['user'],
                                           self.base_fixtures['users'][2]['user']]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(rlc=self.base_fixtures['rlc'], users=users)

    def test_record_message_notification_group(self):
        record: record_models.EncryptedRecord = self.record_fixtures['records'][0]['record']
        notification_groups_start = api_models.NotificationGroup.objects.all().count()
        notifications_start = api_models.Notification.objects.all().count()

        private_key: bytes = self.base_fixtures['users'][0]['private']
        client: APIClient = self.base_fixtures['users'][0]['client']

        # post new record message
        response: Response = client.post('/api/records/e_record/' + str(record.id) + '/messages',
                                         {'message': 'secret message'},
                                         **{'HTTP_PRIVATE_KEY': private_key})
        self.assertEqual(200, response.status_code)

        # 2 because record send notification to 2 other users (1 and 2) (0 causes it)
        self.assertEqual(notification_groups_start + 2, api_models.NotificationGroup.objects.all().count())
        self.assertEqual(notifications_start + 2, api_models.Notification.objects.all().count())

        self.assertEqual(1, api_models.NotificationGroup.objects.filter(
            user=self.base_fixtures['users'][1]['user']).count())
        self.assertEqual(1, api_models.NotificationGroup.objects.filter(
            user=self.base_fixtures['users'][2]['user']).count())
        self.assertEqual(1, api_models.Notification.objects.filter(
            notification_group__user=self.base_fixtures['users'][1]['user']).count())
        self.assertEqual(1, api_models.Notification.objects.filter(
            notification_group__user=self.base_fixtures['users'][2]['user']).count())

        notification_group_from_db: api_models.NotificationGroup = api_models.NotificationGroup.objects.filter(
            user=self.base_fixtures['users'][1]['user']).first()
        self.assertEqual(record.record_token, notification_group_from_db.ref_text)
        self.assertEqual(False, notification_group_from_db.read)
        self.assertEqual(1, notification_group_from_db.notifications.count())
        notification: api_models.Notification = notification_group_from_db.notifications.first()
        self.assertEqual(self.base_fixtures['users'][0]['user'], notification.source_user)
        self.assertEqual(NotificationType.RECORD__RECORD_MESSAGE_ADDED.value, notification.type)

        # new notification, but no new group
        response: Response = client.post('/api/records/e_record/' + str(record.id) + '/messages',
                                         {'message': 'secret message'},
                                         **{'HTTP_PRIVATE_KEY': private_key})
        self.assertEqual(200, response.status_code)

        self.assertEqual(notification_groups_start + 2, api_models.NotificationGroup.objects.all().count())
        self.assertEqual(notifications_start + 4, api_models.Notification.objects.all().count())

        # group updated
        notification_group_from_db_later: api_models.NotificationGroup = api_models.NotificationGroup.objects.filter(
            user=self.base_fixtures['users'][1]['user']).first()
        self.assertFalse(notification_group_from_db_later.last_activity == notification_group_from_db.last_activity)
        self.assertTrue(notification_group_from_db_later.last_activity > notification_group_from_db.last_activity)

        # single notification
        new_notification_from_db: api_models.Notification = notification_group_from_db.notifications.filter(
            ~Q(id=notification.id)).first()
        self.assertEqual(self.base_fixtures['users'][0]['user'], new_notification_from_db.source_user)
        self.assertEqual(NotificationType.RECORD__RECORD_MESSAGE_ADDED.value, new_notification_from_db.type)

    def test_login_notification_groups(self):
        # TODO: generate notification groups from fixtures
        notification: api_models.Notification = api_models.Notification.objects.filter(
            user__email='user1@law-orga.de').first()
        notification.read = True
        notification.save()

        login_response: Response = APIClient().post('/api/login/',
                                                    {'username': 'user1@law-orga.de', 'password': 'qwe123'})
        self.assertEqual(200, login_response.status_code)
        self.assertIn('notifications', login_response.data)
        self.assertEqual(103, login_response.data['notifications'])



        # TODO: check login afterwards

        # TODO: check if read works (all single notifications -> group too)

        # TODO: check get notifications

        # TODO: check read notification and read notification group

        # TODO: check other notifcation sources... A LOT
            # check record updated
            # check new record (consultants)
            # check group member added /removed
            # check group permission request
            # check group deletion request
            # check new user request
            #
