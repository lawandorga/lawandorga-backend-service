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

from backend.api.models import UserEncryptionKeys, UserProfile, Rlc, RlcEncryptionKeys, UsersRlcKeys
from backend.recordmanagement.models import EncryptedClient, EncryptedRecord, Record, RecordEncryption
from backend.recordmanagement.serializers import EncryptedRecordFullDetailSerializer
from backend.static.encryption import AESEncryption, RSAEncryption


class OneTimeGenerators:
    @staticmethod
    def generate_encryption_keys_for_all_users():
        users = UserProfile.objects.all()
        for user in users:
            if UserEncryptionKeys.objects.filter(user=user):
                continue
            private, public = RSAEncryption.generate_keys()
            user_keys = UserEncryptionKeys(user=user, private_key=private, public_key=public)
            user_keys.save()

    @staticmethod
    def generate_encryption_keys_for_rlc():
        rlcs = Rlc.objects.all()
        for rlc in rlcs:
            if RlcEncryptionKeys.objects.filter(rlc=rlc):
                continue
            aes_key = AESEncryption.generate_secure_key()
            private, public = RSAEncryption.generate_keys()
            encrypted_private = AESEncryption.encrypt(private, aes_key)
            rlc_keys = RlcEncryptionKeys(rlc=rlc, encrypted_private_key=encrypted_private, public_key=public)
            rlc_keys.save()

            users_from_rlc = rlc.get_users_from_rlc()
            for user in users_from_rlc:
                users_public = user.get_public_key()
                for_user_encrypted_rlc_aes_key = RSAEncryption.encrypt(aes_key, users_public)
                user_rlc_keys = UsersRlcKeys(user=user, rlc=rlc, encrypted_key=for_user_encrypted_rlc_aes_key)
                user_rlc_keys.save()


class Migrators:
    @staticmethod
    def encrypt_records():
        records = Record.objects.all()
        for record in records:
            record_key = AESEncryption.generate_secure_key()
            client_key = AESEncryption.generate_secure_key()
            client = record.client
            # TODO: ! encryption, potentially search for client (maybe 2nd record for him)
            e_client = EncryptedClient(from_rlc=client.from_rlc, created_on=client.created_on,
                                       last_edited=client.last_edited, birthday=client.birthday,
                                       origin_country=client.origin_country)
            e_client.name = AESEncryption.encrypt(client.name, client_key)
            e_client.note = AESEncryption.encrypt(client.note, client_key)
            e_client.phone_number = AESEncryption.encrypt(client.phone_number, client_key)
            e_client.save()

            # encrypt client_encryption_key with rlc's public key
            if client.from_rlc:
                rlc = client.from_rlc
            elif record.from_rlc:
                rlc = record.from_rlc
            rlc_public_key = rlc.get_public_key()
            e_client.encrypted_client_key = RSAEncryption.encrypt(client_key, rlc_public_key)
            e_client.save()

            e_record = EncryptedRecord(creator=record.creator, from_rlc=record.from_rlc, created_on=record.created_on,
                                       last_edited=record.last_edited, client=e_client,
                                       first_contact_date=record.first_contact_date,
                                       last_contact_date=record.last_contact_date,
                                       first_consultation=record.first_consultation, record_token=record.record_token,
                                       official_note=record.official_note, state=record.state)
            e_record.save()
            # tags
            for tag in record.tagged.all():
                e_record.tagged.add(tag)
            # working on
            for user in record.working_on_record.all():
                e_record.working_on_record.add(user)
            e_record.save()

            if record.note:
                e_record.note = AESEncryption.encrypt(record.note, record_key)
            if record.consultant_team:
                e_record.consultant_team = AESEncryption.encrypt(record.consultant_team, record_key)
            if record.lawyer:
                e_record.lawyer = AESEncryption.encrypt(record.lawyer, record_key)
            if record.related_persons:
                e_record.related_persons = AESEncryption.encrypt(record.related_persons, record_key)
            if record.contact:
                e_record.contact = AESEncryption.encrypt(record.contact, record_key)
            if record.bamf_token:
                e_record.bamf_token = AESEncryption.encrypt(record.bamf_token, record_key)
            if record.foreign_token:
                e_record.foreign_token = AESEncryption.encrypt(record.foreign_token, record_key)
            if record.first_correspondence:
                e_record.first_correspondence = AESEncryption.encrypt(record.first_correspondence, record_key)
            if record.circumstances:
                e_record.circumstances = AESEncryption.encrypt(record.circumstances, record_key)
            if record.next_steps:
                e_record.next_steps = AESEncryption.encrypt(record.next_steps, record_key)
            if record.status_described:
                e_record.status_described = AESEncryption.encrypt(record.status_described, record_key)
            if record.additional_facts:
                e_record.additional_facts = AESEncryption.encrypt(record.additional_facts, record_key)
            e_record.save()

            # messages

            # documents

            # record permissions

            # test data = EncryptedRecordFullDetailSerializer(e_record).get_decrypted_data(record_key)

            # TODO: add encryption keys for all users
            users_with_permission = e_record.get_users_with_decryption_keys()
            for user in users_with_permission:
                users_public_key = user.get_public_key()
                encrypted_record_key = RSAEncryption.encrypt(record_key, users_public_key)
                record_encryption = RecordEncryption(user=user, record=e_record, encrypted_key=encrypted_record_key)
                record_encryption.save()
