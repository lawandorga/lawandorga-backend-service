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
from rest_framework.test import APIClient

from backend.api import models as api_models
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement import models as record_models


class NotificationTest(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [self.base_fixtures['users'][0]['user'],
                                           self.base_fixtures['users'][1]['user'],
                                           self.base_fixtures['users'][2]['user']]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(rlc=self.base_fixtures['rlc'], users=users)

        # record permissions
        # user 0 can create records
        # add_record_permission = api_models.Permission.objects.get(name=permissions.PERMISSION_CAN_ADD_RECORD_RLC)
        # has_perm = api_models.HasPermission(permission=add_record_permission,
        #                                     user_has_permission=self.base_fixtures['users'][0]['user'],
        #                                     permission_for_rlc=self.base_fixtures['rlc'])
        # has_perm.save()
        #
        # # all users from group 0 can consult
        # can_consult_permission = api_models.Permission.objects.get(name=permissions.PERMISSION_CAN_CONSULT)
        # has_perm = api_models.HasPermission(permission=can_consult_permission,
        #                                     group_has_permission=self.base_fixtures['groups'][0],
        #                                     permission_for_rlc=self.base_fixtures['rlc'])
        # has_perm.save()

    def test_record_message_notification(self):
        record: record_models.EncryptedRecord = self.record_fixtures['records'][0]['record']
        before = api_models.Notification.objects.all().count()

        # from fixtures
        private_key: bytes = self.base_fixtures['users'][0]['private']
        client: APIClient = self.base_fixtures['users'][0]['client']

        # post new record message
        client.post('/api/records/e_record/' + str(record.id) + '/messages', {'message': 'secret message'},
                    **{'HTTP_PRIVATE_KEY': private_key})

        # 2 because record send notification to 2 other users (1 causes it)
        self.assertEqual(before + 2, api_models.Notification.objects.all().count())
        notification_for_user_1: api_models.Notification = api_models.Notification.objects.filter(
            user=self.base_fixtures['users'][1]['user']).first()
        self.assertTrue(notification_for_user_1 is not None)
        self.assertEqual(notification_for_user_1.source_user, self.base_fixtures['users'][0]['user'])
        self.assertEqual(notification_for_user_1.read, False)
        self.assertEqual(notification_for_user_1.ref_id, str(record.id))
        self.assertEqual(notification_for_user_1.ref_text, str(record.record_token))

