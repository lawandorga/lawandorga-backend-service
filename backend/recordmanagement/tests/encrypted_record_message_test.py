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


class EncryptedRecordMessageTest(TransactionTestCase):
    def setUp(self) -> None:
        self.base_fixtures = CreateFixtures.create_base_fixtures()
        users: [api_models.UserProfile] = [self.base_fixtures['users'][0]['user'],
                                           self.base_fixtures['users'][1]['user'],
                                           self.base_fixtures['users'][2]['user']]
        self.record_fixtures = CreateFixtures.create_record_base_fixtures(rlc=self.base_fixtures['rlc'], users=users)

    def test_message_creation(self):
        record: record_models.EncryptedRecord = self.record_fixtures['records'][0]['record']
        overall_messages: int = record_models.EncryptedRecordMessage.objects.all().count()
        record_messages: int = record_models.EncryptedRecordMessage.objects.filter(record=record).count()

        # from fixtures
        private_key: bytes = self.base_fixtures['users'][0]['private']
        client: APIClient = self.base_fixtures['users'][0]['client']

        # post new record message
        response = client.post('/api/records/e_record/' + str(record.id) + '/messages', {'message': 'secret message'},
                    **{'HTTP_PRIVATE_KEY': private_key})

        # assert if message is created in db
        self.assertEquals(overall_messages + 1, record_models.EncryptedRecordMessage.objects.all().count())
        self.assertEquals(record_messages + 1,
                          record_models.EncryptedRecordMessage.objects.filter(record=record).count())
        self.assertEquals('secret message', response.data['message'])
