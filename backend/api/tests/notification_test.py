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

from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption
from backend.api.tests.fixtures_encryption import CreateFixtures
from backend.recordmanagement.tests.missing_record_keys_test import MissingRecordKeysTests


class NotificationTest(TransactionTestCase):
    def setUp(self):
        self.base_fixtures = CreateFixtures.create_base_fixtures()

    def create_record_fixture(self):
        return_object = {}

        # create client
        aes_client_key = AESEncryption.generate_secure_key()
        e_client = record_models.EncryptedClient(from_rlc=self.base_fixtures['rlc'])
        e_client.name = AESEncryption.encrypt('MainClient', aes_client_key)
        e_client.note = AESEncryption.encrypt('important MainClient note', aes_client_key)
        e_client.save()
        e_client = e_client
        client_obj = {
            "client": e_client,
            "key": aes_client_key
        }
        return_object.update({"client": client_obj})

        # create records
        records = []
        # 1
        record1 = MissingRecordKeysTests.add_record(token='record1', rlc=self.base_fixtures['rlc'], client=e_client,
                                                    creator=self.base_fixtures['users'][0]['user'],
                                                    note='record1 note',
                                                    working_on_record=[self.base_fixtures['users'][1]['user']],
                                                    with_record_permission=[],
                                                    with_encryption_keys=[self.base_fixtures['users'][0]['user'],
                                                                          self.base_fixtures['users'][2]['user'],
                                                                          self.superuser['user']])
        records.append(record1)
        # 2
        record2 = MissingRecordKeysTests.add_record(token='record2', rlc=self.base_fixtures['rlc'], client=e_client,
                                                    creator=self.base_fixtures['users'][0]['user'],
                                                    note='record2 note',
                                                    working_on_record=[self.base_fixtures['users'][0]['user']],
                                                    with_record_permission=[self.base_fixtures['users'][1]['user']],
                                                    with_encryption_keys=[self.base_fixtures['users'][0]['user']])
        records.append(record2)

        return_object.update({"records": records})

        return return_object

    def first_test(self):
        record_fixtures = self.create_record_fixture()

        record_models.EncryptedRecordMessage()
