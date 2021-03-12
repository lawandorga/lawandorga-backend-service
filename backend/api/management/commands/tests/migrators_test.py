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
import random

from django.test import SimpleTestCase, TransactionTestCase
from backend.api.management.commands._migrators import Migrators
from backend.api.management.commands.commands import populate_deploy_db
from backend.api.tests import CreateFixtures
from backend.recordmanagement.models import OriginCountry, Rlc, EncryptedClient
from backend.api.management.commands.create_dummy_data import (
    Command as CreateDummyCommand,
)


class MigratorsTest(TransactionTestCase):
    def setUp(self) -> None:
        populate_deploy_db()
        self.base_fixtures = CreateFixtures.create_base_fixtures()

    # def test_client_creation(self):
    #     client = (
    #         (2018, 7, 12),  # created_on
    #         (2018, 8, 28, 21, 3, 0, 0),  # last_edited
    #         "Bibi Aisha",  # name
    #         "auf Flucht von Ehemann getrennt worden",  # note
    #         "01793456542",  # phone number
    #         (1990, 5, 1),  # birthday
    #         OriginCountry.objects.first(),  # origin country id
    #     )
    #     clients_before = EncryptedClient.objects.count()
    #     CreateDummyCommand().get_and_create_client(client, self.base_fixtures["rlc"])
    #     self.assertEqual(clients_before + 1, EncryptedClient.objects.count())

    # def test_client_retrieval(self):
    #     self.test_client_creation()
    #     client = EncryptedClient.objects.first()
    #     rlc_private = self.base_fixtures["users"][0]["user"].get_rlcs_private_key(
    #         self.base_fixtures["users"][0]["private"]
    #     )
    #     client_dict = client.get_decrypted(rlc_private)
    #     self.assertEqual("auf Flucht von Ehemann getrennt worden", client_dict["note"])
