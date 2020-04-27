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

from backend.api import models as api_models
from backend.recordmanagement import models as record_models
from backend.static.permissions import get_record_encryption_keys_permissions_strings


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
            get_record_encryption_keys_permissions_strings(), for_rlc=rlc)
        # iterate over records
        records = record_models.EncryptedRecord.objects.filter(from_rlc=rlc)
        for record in records:
            # get all users with permission for record: overall + working on + record permission
            users_with_record_permission = api_models.UserProfile.objects.filter(
                e_record_permissions_requested__record=record,
                e_record_permissions_requested__state='gr')
            users_with_keys = record.working_on_record.all().union(users_with_record_permission).union(
                users_with_decryption_key_permissions).union(superusers).distinct()
            # iterate over users
            for user in users_with_keys:
                # check if record encryption entry exists
                keys = record_models.RecordEncryption.objects.filter(record=record, user=user).count()
                if not keys > 0:
                    # NO: check if missing record key entry exists
                    missing_keys = record_models.MissingRecordKey.objects.filter(record=record, user=user).count()
                    if not missing_keys > 0:
                        # NO: add new missing key entry
                        missing_key = record_models.MissingRecordKey(record=record, user=user)
                        missing_key.save()
