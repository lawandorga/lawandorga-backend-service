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
        self.assertEqual(NotificationType.RECORD_MESSAGE.value, notification.sub_type)

        response: Response = client.post('/api/records/e_record/' + str(record.id) + '/messages',
                                         {'message': 'secret message'},
                                         **{'HTTP_PRIVATE_KEY': private_key})
        self.assertEqual(200, response.status_code)

        self.assertEqual(notification_groups_start + 2, api_models.NotificationGroup.objects.all().count())
        self.assertEqual(notifications_start + 4, api_models.Notification.objects.all().count())

        notification_group_from_db_later: api_models.NotificationGroup = api_models.NotificationGroup.objects.filter(
            user=self.base_fixtures['users'][1]['user']).first()
        self.assertFalse(notification_group_from_db_later.last_activity == notification_group_from_db.last_activity)
        self.assertTrue(notification_group_from_db_later.last_activity > notification_group_from_db.last_activity)

        # notification_for_user_1: api_models.Notification = api_models.Notification.objects.filter(
        #     user=self.base_fixtures['users'][1]['user']).first()
        # self.assertTrue(notification_for_user_1 is not None)
        # self.assertEqual(notification_for_user_1.source_user, self.base_fixtures['users'][0]['user'])
        # self.assertEqual(notification_for_user_1.read, False)
        # self.assertEqual(notification_for_user_1.ref_id, str(record.id))

        # TODO: check if new single notifications gets added to group and gruop last activity gets updated



        # TODO: created notification group, created notifications, check group itself and check notifications itself (if correct)

        # TODO: check login afterwards

        # TODO: check if read works (all single notifications -> group too)


        # TODO: check other notifcation sources... A LOT
        # TODO: check record updated
