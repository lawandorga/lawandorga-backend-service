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

from backend.api.models import Rlc, RlcEncryptionKeys, UserEncryptionKeys, UserProfile, UsersRlcKeys
from backend.recordmanagement.models import EncryptedClient, EncryptedRecord, EncryptedRecordDeletionRequest, \
    EncryptedRecordDocument, EncryptedRecordMessage, EncryptedRecordPermission, Record, RecordDeletionRequest, \
    RecordDocument, RecordEncryption, RecordMessage, RecordPermission
from backend.static.encrypted_storage import EncryptedStorage
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.file_utils import delete_file


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
    def encrypt_all_records():
        records = Record.objects.all()
        for record in records:
            Migrators.encrypt_record(record)

    @staticmethod
    def encrypt_record(record):
        e_record_key = AESEncryption.generate_secure_key()
        client_key = AESEncryption.generate_secure_key()
        client = record.client
        potential_e_client = EncryptedClient.objects.filter(from_rlc=client.from_rlc, created_on=client.created_on,
                                                            birthday=client.birthday).first()
        if not potential_e_client:
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
        else:
            e_client = potential_e_client

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

        AESEncryption.encrypt_field(record, e_record, 'note', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'consultant_team', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'lawyer', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'related_persons', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'contact', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'bamf_token', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'foreign_token', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'first_correspondence', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'circumstances', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'next_steps', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'status_described', e_record_key)
        AESEncryption.encrypt_field(record, e_record, 'additional_facts', e_record_key)
        e_record.save()

        # messages
        messages = RecordMessage.objects.filter(record=record)
        for message in messages:
            e_message = EncryptedRecordMessage(sender=message.sender, record=e_record,
                                               created_on=message.created_on)
            AESEncryption.encrypt_field(message, e_message, 'message', e_record_key)
            e_message.save()

        # documents
        documents = RecordDocument.objects.filter(record=record)
        if documents:
            print('record with documents: ' + str(e_record))
        for document in documents:
            Migrators.decrypt_record_document(document, e_record, e_record_key)

        # record permissions
        permissions = RecordPermission.objects.filter(record=record)
        for permission in permissions:
            e_permission = EncryptedRecordPermission(request_from=permission.request_from,
                                                     request_processed=permission.request_processed,
                                                     record=e_record, requested=permission.requested,
                                                     processed_on=permission.processed_on,
                                                     can_edit=permission.can_edit, state=permission.state)
            e_permission.save()
        users_with_permission = e_record.get_users_with_decryption_keys()
        for user in users_with_permission:
            users_public_key = user.get_public_key()
            encrypted_record_key = RSAEncryption.encrypt(e_record_key, users_public_key)
            record_encryption = RecordEncryption(user=user, record=e_record, encrypted_key=encrypted_record_key)
            record_encryption.save()

        # record deletions
        deletion_requests = RecordDeletionRequest.objects.filter(record=record)
        for deletion_request in deletion_requests:
            e_deletion_request = EncryptedRecordDeletionRequest(request_from=deletion_request.request_from,
                                                                request_processed=deletion_request.request_processed,
                                                                record=e_record,
                                                                explanation=deletion_request.explanation,
                                                                requested=deletion_request.requested,
                                                                processed_on=deletion_request.processed_on,
                                                                state=deletion_request.state)
            e_deletion_request.save()

    @staticmethod
    def decrypt_record_document(record_document, e_record, e_record_key):
        e_record_document = EncryptedRecordDocument(record=e_record, creator=record_document.creator,
                                                    name=record_document.name, created_on=record_document.created_on,
                                                    last_edited=record_document.last_edited,
                                                    file_size=record_document.file_size)
        e_record_document.save()
        for tag in record_document.tagged.all():
            e_record_document.tagged.add(tag)
        e_record_document.save()

        # download file
        local_path_to_file = 'temp/' + record_document.name
        try:
            print('file to download:', record_document.get_file_key())
            EncryptedStorage.download_file_from_s3(record_document.get_file_key(), local_path_to_file)
        except Exception as e:
            # fakefile in dummy rlc
            print('record document: ' + str(record_document) + ' doesn\'t seem to exist')
            print('error: ', e)

            return
        # encrypt file and upload to s3
        EncryptedStorage.encrypt_file_and_upload_to_s3(local_path_to_file, e_record_key,
                                                       e_record_document.get_folder())
        # delete old
        delete_file(local_path_to_file)
        delete_file(local_path_to_file + '.enc')
