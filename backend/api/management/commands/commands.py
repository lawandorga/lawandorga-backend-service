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
from backend.api import models as api_models
from backend.recordmanagement import models as record_models
from backend.api.management.commands._migrators import Migrators, OneTimeGenerators
from backend.static.permissions import get_record_encryption_keys_permissions_strings
from backend.api.models import *
from backend.recordmanagement.models import *
from backend.api.management.commands.fixtures import Fixtures
from backend.files.models import *
from backend.api.tests.example_data import create


def create_missing_key_entries():
    """
    searches database for missing keys entries for records and insert them in database
    :return:
    """
    # iterate over rlcs
    superusers = api_models.UserProfile.objects.filter(is_superuser=True)
    rlcs = api_models.Rlc.objects.all()
    for rlc in rlcs:
        # get users with overall permission for rlc
        users_with_decryption_key_permissions = api_models.UserProfile.objects.get_users_with_special_permissions(
            get_record_encryption_keys_permissions_strings(), for_rlc=rlc
        )
        # iterate over records
        records = record_models.EncryptedRecord.objects.filter(from_rlc=rlc)
        for record in records:
            # get all users with permission for record: overall + working on + record permission
            users_with_record_permission = api_models.UserProfile.objects.filter(
                e_record_permissions_requested__record=record,
                e_record_permissions_requested__state="gr",
            )
            users_with_keys = (
                record.working_on_record.all()
                .union(users_with_record_permission)
                .union(users_with_decryption_key_permissions)
                .union(superusers)
                .distinct()
            )
            # iterate over users
            for user in users_with_keys:
                # check if record encryption entry exists
                keys = record_models.RecordEncryption.objects.filter(
                    record=record, user=user
                ).count()
                if not keys > 0:
                    # NO: check if missing record key entry exists
                    missing_keys = record_models.MissingRecordKey.objects.filter(
                        record=record, user=user
                    ).count()
                    if not missing_keys > 0:
                        # NO: add new missing key entry
                        missing_key = record_models.MissingRecordKey(
                            record=record, user=user
                        )
                        missing_key.save()


# def create_missing_rlc_keys_entries():
# TODO?


def migrate_to_encryption():
    reset_db_encrypted()
    # EncryptedClient.objects.all().delete()
    # EncryptedRecord.objects.all().delete()
    # EncryptedRecordPermission.objects.all().delete()
    # EncryptedRecordMessage.objects.all().delete()
    # EncryptedRecordDocument.objects.all().delete()
    # EncryptedRecordDeletionRequest.objects.all().delete()
    #
    # UserEncryptionKeys.objects.all().delete()
    # RlcEncryptionKeys.objects.all().delete()
    # RecordEncryption.objects.all().delete()
    # UsersRlcKeys.objects.all().delete()

    OneTimeGenerators.generate_encryption_keys_for_all_users()
    OneTimeGenerators.generate_encryption_keys_for_rlc()
    Migrators.encrypt_all_records()


def aws_environment_variables_viable(command):
    if settings.SCW_SECRET_KEY:
        command.stdout.write("secret key: " + settings.SCW_SECRET_KEY, ending="")
    else:
        command.stdout.write("s3 secret key not found!")
        return False

    if settings.SCW_ACCESS_KEY:
        command.stdout.write("scw access key: " + settings.SCW_ACCESS_KEY, ending="")
    else:
        command.stdout.write("scw access key not found!")
        return False

    if settings.SCW_S3_BUCKET_NAME:
        command.stdout.write(
            "scw bucket name: " + settings.SCW_S3_BUCKET_NAME, ending=""
        )
    else:
        command.stdout.write("scw bucket name not found!")
        return False

    return True


def add_permissions():
    Fixtures.create_real_permissions_no_duplicates()
    Fixtures.create_real_folder_permissions_no_duplicate()


def migrate_to_rlc_settings():
    # RlcSettings.objects.all().delete()
    OneTimeGenerators.generate_rlc_settings_for_rlc()


def reset_db():
    # UserProfile.objects.exclude(is_superuser=True).delete()
    UserProfile.objects.all().delete()
    Client.objects.all().delete()
    OriginCountry.objects.all().delete()
    RecordTag.objects.all().delete()
    Record.objects.all().delete()
    Group.objects.all().delete()
    HasPermission.objects.all().delete()
    Permission.objects.all().delete()
    Rlc.objects.all().delete()
    RecordMessage.objects.all().delete()
    RecordDocument.objects.all().delete()
    RecordDocumentTag.objects.all().delete()
    RecordPermission.objects.all().delete()
    ForgotPasswordLinks.objects.all().delete()
    NewUserRequest.objects.all().delete()
    UserActivationLink.objects.all().delete()
    RecordDeletionRequest.objects.all().delete()
    File.objects.all().delete()
    Folder.objects.all().delete()
    FolderPermission.objects.all().delete()
    PermissionForFolder.objects.all().delete()
    Notification.objects.all().delete()
    NotificationGroup.objects.all().delete()
    reset_db_encrypted()


def reset_db_encrypted():
    EncryptedClient.objects.all().delete()
    EncryptedRecord.objects.all().delete()
    EncryptedRecordPermission.objects.all().delete()
    EncryptedRecordMessage.objects.all().delete()
    EncryptedRecordDocument.objects.all().delete()
    EncryptedRecordDeletionRequest.objects.all().delete()

    UserEncryptionKeys.objects.all().delete()
    RlcEncryptionKeys.objects.all().delete()
    RecordEncryption.objects.all().delete()
    UsersRlcKeys.objects.all().delete()
    MissingRlcKey.objects.all().delete()
    MissingRecordKey.objects.all().delete()


def populate_deploy_db():
    Fixtures.create_real_tags()
    Fixtures.create_real_document_tags()
    Fixtures.create_real_origin_countries()
    add_permissions()


def delete_all_missing_record_key_entries():
    MissingRecordKey.objects.all().delete()


def delete_all_missing_rlc_key_entries():
    MissingRlcKey.objects.all().delete()


def delete_all_forgot_password_links():
    ForgotPasswordLinks.objects.all().delete()


def create_dummy_data():
    create()
