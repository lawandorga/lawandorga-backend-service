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

from django.conf import settings
from django.core.management.base import BaseCommand

from backend.api.management.commands._migrators import Migrators, OneTimeGenerators
from backend.api.models import RlcEncryptionKeys, UserEncryptionKeys
from backend.recordmanagement.models import EncryptedClient, EncryptedRecord, EncryptedRecordDeletionRequest, \
    EncryptedRecordDocument, EncryptedRecordMessage, EncryptedRecordPermission, RecordEncryption


class Command(BaseCommand):
    help = 'migrates all existing data to encrypted, adds encryption keys to users and ' \
           'encrypts records with corresponding files'

    def handle(self, *args, **options):
        EncryptedClient.objects.all().delete()
        EncryptedRecord.objects.all().delete()
        EncryptedRecordPermission.objects.all().delete()
        EncryptedRecordMessage.objects.all().delete()
        EncryptedRecordDocument.objects.all().delete()
        EncryptedRecordDeletionRequest.objects.all().delete()

        UserEncryptionKeys.objects.all().delete()
        RlcEncryptionKeys.objects.all().delete()
        RecordEncryption.objects.all().delete()

        # self.stdout.write("test", ending='')
        # self.stdout.write(options['admin_password'], ending='')
        # self.stdout.write(options['rlc_name'], ending='')

        env_valid = self.aws_environment_variables_viable()
        if not env_valid:
            return

        OneTimeGenerators.generate_encryption_keys_for_all_users()
        OneTimeGenerators.generate_encryption_keys_for_rlc()
        Migrators.encrypt_all_records()

    def aws_environment_variables_viable(self):
        if settings.AWS_S3_BUCKET_NAME:
            self.stdout.write("s3bucket: " + settings.AWS_S3_BUCKET_NAME, ending='')
        else:
            self.stdout.write("s3 bucket not found!")
            return False

        if settings.AWS_S3_REGION_NAME:
            self.stdout.write("s3 region name: " + settings.AWS_S3_REGION_NAME, ending='')
        else:
            self.stdout.write("s3 region not found!")
            return False

        if settings.AWS_ACCESS_KEY_ID:
            self.stdout.write("s3 access key id: " + settings.AWS_ACCESS_KEY_ID, ending='')
        else:
            self.stdout.write("s3 access key not found!")
            return False

        if settings.AWS_SECRET_ACCESS_KEY:
            self.stdout.write("s3 secret access key id: " + settings.AWS_SECRET_ACCESS_KEY, ending='')
        else:
            self.stdout.write("s3 secret access key not found!")
            return False
        return True
