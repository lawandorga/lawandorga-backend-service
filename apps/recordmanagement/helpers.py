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
from apps.recordmanagement.models import EncryptedRecord, RecordEncryption
from apps.static.encryption import RSAEncryption


def check_encryption_key_holders_and_grant(granting_user, granting_users_private_key):
    # TODO: refactor and check, maybe raise error?
    records = EncryptedRecord.objects.filter(from_rlc=granting_user.rlc)
    for record in records:
        try:
            record_key = record.get_decryption_key(
                granting_user, granting_users_private_key
            )
        # TODO: don't do this
        except Exception:
            continue
        users_with_keys = record.get_users_who_should_be_allowed_to_decrypt()
        for user in users_with_keys:

            if not RecordEncryption.objects.filter(user=user, record=record).exists():
                users_public_key = user.get_public_key()
                encrypted_record_key = RSAEncryption.encrypt(
                    record_key, users_public_key
                )
                record_encryption = RecordEncryption(
                    user=user, record=record, encrypted_key=encrypted_record_key
                )
                record_encryption.save()
