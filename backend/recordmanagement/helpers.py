#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
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

from backend.recordmanagement.models import (
    EncryptedRecord,
    RecordEncryption,
    MissingRecordKey,
)
from backend.api.models import UserEncryptionKeys
from backend.static.encryption import RSAEncryption


def add_record_encryption_keys_for_users(
    granting_user, granting_users_private_key, users_to_give
):
    # TODO: refactor and check, maybe raise error?
    records = EncryptedRecord.objects.filter(from_rlc=granting_user.rlc)
    for record in records:
        record_key = record.get_decryption_key(
            granting_user, granting_users_private_key
        )
        for member in users_to_give:
            try:
                already_existing = RecordEncryption.objects.get(
                    user=member, record=record
                )
            except:
                members_public_key = member.get_public_key()
                encrypted_record_key = RSAEncryption.encrypt(
                    record_key, members_public_key
                )
                record_encryption = RecordEncryption(
                    user=member, record=record, encrypted_key=encrypted_record_key
                )
                record_encryption.save()


def check_encryption_key_holders_and_grant(granting_user, granting_users_private_key):
    # TODO: refactor and check, maybe raise error?
    records = EncryptedRecord.objects.filter(from_rlc=granting_user.rlc)
    for record in records:
        record_key = record.get_decryption_key(
            granting_user, granting_users_private_key
        )
        users_with_keys = record.get_users_with_decryption_keys()
        for user in users_with_keys:
            try:
                already_existing = RecordEncryption.objects.get(
                    user=user, record=record
                )
            except:
                users_public_key = UserEncryptionKeys.objects.get_users_public_key(user)
                encrypted_record_key = RSAEncryption.encrypt(
                    record_key, users_public_key
                )
                record_encryption = RecordEncryption(
                    user=user, record=record, encrypted_key=encrypted_record_key
                )
                record_encryption.save()


def resolve_missing_record_key_entries(user, users_private_key):
    missing_keys = MissingRecordKey.objects.filter(record__from_rlc=user.rlc)
    for missing_key in missing_keys:
        mine = RecordEncryption.objects.filter(
            record=missing_key.record, user=user
        ).first()
        if mine:
            try:
                missing_key_users_public_key = UserEncryptionKeys.objects.get_users_public_key(
                    missing_key.user
                )
                record_key = mine.decrypt(users_private_key)
                encrypted_record_key = RSAEncryption.encrypt(
                    record_key, missing_key_users_public_key
                )
                new_key = RecordEncryption(
                    user=missing_key.user,
                    record=missing_key.record,
                    encrypted_key=encrypted_record_key,
                )
                new_key.save()
                missing_key.delete()
            except Exception as e:
                pass
