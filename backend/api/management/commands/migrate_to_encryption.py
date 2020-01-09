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

from django.core.management.base import BaseCommand

from backend.api.management.commands._migrators import OneTimeGenerators, Migrators
from backend.api.models import RlcEncryptionKeys
from backend.recordmanagement.models import EncryptedClient, EncryptedRecord


class Command(BaseCommand):
    help = 'migrates all existing data to encrypted, adds encryption keys to users and ' \
           'encrypts records with corresponding files'

    def handle(self, *args, **options):
        EncryptedClient.objects.all().delete()
        EncryptedRecord.objects.all().delete()
        RlcEncryptionKeys.objects.all().delete()
        # self.stdout.write("test", ending='')
        # self.stdout.write(options['admin_password'], ending='')
        # self.stdout.write(options['rlc_name'], ending='')

        OneTimeGenerators.generate_encryption_keys_for_all_users()
        OneTimeGenerators.generate_encryption_keys_for_rlc()
        Migrators.encrypt_records()
