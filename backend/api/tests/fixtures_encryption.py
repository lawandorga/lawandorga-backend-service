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

from rest_framework.test import APIClient

from backend.api.models import Group, Permission, Rlc, RlcEncryptionKeys, UserEncryptionKeys, UserProfile, UsersRlcKeys
from backend.files import models as file_models
from backend.files.static.folder_permissions import get_all_folder_permissions_strings
from backend.recordmanagement import models as record_models
from backend.static.encryption import AESEncryption, RSAEncryption
from backend.static.permissions import get_all_permissions_strings
from backend.api.management.commands._fixtures import Fixtures


class CreateFixtures:
    @staticmethod
    def create_base_fixtures() -> {'rlc': Rlc, 'users': [{'user': UserProfile, 'private': bytes, 'client': APIClient}],
                                   'groups': [Group]}:
        """
        creates Basic fixtures for testing purposes
        creates all permissions, 1 rlc, 4 users and 3 groups

        usage examples:
        {return_object}['rlc']: Rlc
        {return_object}['users'][1]['user']: UserProfile

        :return: objects with following structure
        rlc: Rlc
        users
            - user 1
                user: UserProfile
                private: Bytes, Private Key of User
                client: ApiClient with authenticated User
            - user 2, 3 4
        groups
            - group 1,2,3: Group

        """
        CreateFixtures.create_permissions()
        Fixtures.create_real_tags()
        Fixtures.create_real_document_tags()
        Fixtures.create_real_origin_countries()

        return_object = {}

        rlc = Rlc(name="testrlc", id=3001)
        rlc.save()
        rlc_aes_key = 'SecureAesKey'
        private, public = RSAEncryption.generate_keys()
        encrypted_private = AESEncryption.encrypt(private, rlc_aes_key)
        rlc_keys = RlcEncryptionKeys(rlc=rlc, encrypted_private_key=encrypted_private, public_key=public)
        rlc_keys.save()
        return_object.update({"rlc": rlc})

        users = [CreateFixtures.create_user(rlc, "user1", rlc_aes_key),
                 CreateFixtures.create_user(rlc, "user2", rlc_aes_key),
                 CreateFixtures.create_user(rlc, "user3", rlc_aes_key),
                 CreateFixtures.create_user(rlc, "user4", rlc_aes_key)]
        return_object.update({"users": users})

        groups = [CreateFixtures._create_group(rlc, 'group1', [users[0]['user'], users[1]['user']]),
                  CreateFixtures._create_group(rlc, 'group2', [users[1]['user'], users[2]['user']]),
                  CreateFixtures._create_group(rlc, 'group3', [users[2]['user'], users[3]['user']])]
        return_object.update({'groups': groups})

        return return_object

    @staticmethod
    def create_user(rlc: Rlc, name: str, rlc_aes_key: str) -> {'user': UserProfile, 'private': bytes,
                                                               'client': APIClient}:
        """
        creates user with given parameters and generic email

        :param rlc: Rlc, rlc of user
        :param name: str, name of user
        :param rlc_aes_key: str, encryption key for rlc
        :return: object with following structure
        user: UserProfile
        private: bytes, users private key
        client: ApiClient, ApiClient with authenticated user
        """
        user = UserProfile(name=name, email=name + "@law-orga.de", rlc=rlc)
        user.set_password("qwe123")
        user.save()
        private, public = RSAEncryption.generate_keys()
        keys = UserEncryptionKeys(user=user, private_key=private, public_key=public)
        keys.save()

        encrypted_rlcs_key = RSAEncryption.encrypt(rlc_aes_key, public)
        rlcs_keys = UsersRlcKeys(user=user, rlc=rlc, encrypted_key=encrypted_rlcs_key)
        rlcs_keys.save()

        client = APIClient()
        client.force_authenticate(user=user)
        return {
            "user": user,
            "private": private,
            "client": client
        }

    @staticmethod
    def _create_group(rlc: Rlc, name: str, members: [UserProfile]) -> Group:
        """
        creates generic group with given params

        :param rlc: Rlc, rlc to which the group belongs to
        :param name: str, name of the group
        :param members: [UserProfile], UserProfiles which should be added to the group
        :return: Group, the created group
        """
        group = Group(name=name, from_rlc=rlc, visible=True)
        group.save()

        for member in members:
            group.group_members.add(member)
        return group

    @staticmethod
    def create_permissions() -> None:
        """
        creates all permissions and folder permissions
        :return: None
        """
        perms = get_all_permissions_strings()
        for perm in perms:
            Permission.objects.create(name=perm)
        perms = get_all_folder_permissions_strings()
        for perm in perms:
            file_models.FolderPermission.objects.create(name=perm)

    @staticmethod
    def create_superuser() -> {'user': UserProfile, 'private': bytes, 'client': APIClient}:
        """
        creates superuser with generic information

        :return: object with following structure:
        user: UserProfile, user object of created superuser
        private: bytes, private key of superuser
        client: ApiClient, ApiClient with authenticated superuser
        """
        superuser = UserProfile(name='superuser', email='superuser@test.de', is_superuser=True)
        superuser.set_password('qwe123')
        superuser.save()
        private, public = RSAEncryption.generate_keys()
        keys = UserEncryptionKeys(user=superuser, private_key=private, public_key=public)
        keys.save()
        client = APIClient()
        client.force_authenticate(user=superuser)
        return {
            "user": superuser,
            "private": private,
            "client": client
        }

    @staticmethod
    def create_record_base_fixtures(rlc: Rlc, users: [UserProfile]):
        """
        Creates 2 basic record with encryption keys for each user

        record 1: user 1 and 2 working on, user 3 has permission
        record 2: user 2 and 3 working on, user 1 has permission


        :param rlc: rlc of records and users
        :param users: 3 users which are used as consultants and record_permission holders for records
        :return: object with following structure
        client
            - client: Client
            - key: Bytes, Clients Aes Key
        records
            - record 1 2
        """
        return_object = {}

        aes_client_key = AESEncryption.generate_secure_key()
        e_client = record_models.EncryptedClient(from_rlc=rlc)
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
        record1 = CreateFixtures.add_record(record_token='record1', rlc=rlc, client=e_client,
                                            creator=users[0],
                                            note='record1 note',
                                            working_on_record=[users[0], users[1]],
                                            with_record_permission=[users[2]],
                                            with_encryption_keys=[users[0], users[1], users[2]])
        records.append(record1)
        # 2
        record2 = CreateFixtures.add_record(record_token='record2', rlc=rlc, client=e_client,
                                            creator=users[1],
                                            note='record2 note',
                                            working_on_record=[users[1], users[2]],
                                            with_record_permission=[users[0]],
                                            with_encryption_keys=[users[0], users[1], users[2]])
        records.append(record2)

        return_object.update({"records": records})

        return return_object

    @staticmethod
    def add_record(record_token: str, rlc: Rlc, client: record_models.EncryptedClient, creator: UserProfile, note: str,
                   working_on_record: [UserProfile], with_record_permission: [UserProfile] = [],
                   with_encryption_keys: [UserProfile] = []) -> {'record': record_models.EncryptedRecord, 'key': str}:
        """
        adds record with given parameters to database
        record_permissions and encryption_key holders can be specified separately

        :param record_token:
        :param rlc:
        :param client:
        :param creator:
        :param note:
        :param working_on_record: list of users which are working on record
        :param with_record_permission: list of users with granted record permissions
        :param with_encryption_keys: list of users with encryption keys
        :return: object with structure:
        record: Record
        key: aes key
        """
        aes_key = AESEncryption.generate_secure_key()
        record = record_models.EncryptedRecord(record_token=record_token, from_rlc=rlc,
                                               creator=creator, client=client)
        record.note = AESEncryption.encrypt(note, aes_key)
        record.save()

        for user in working_on_record:
            record.working_on_record.add(user)
        record.save()

        for user in with_record_permission:
            permission = record_models.EncryptedRecordPermission(request_from=user, request_processed=creator,
                                                                 record=record, can_edit=True, state='gr')
            permission.save()

        for user in with_encryption_keys:
            CreateFixtures.add_encryption_key(user, record, aes_key)

        return {
            'record': record,
            'key': aes_key
        }

    @staticmethod
    def add_encryption_key(user: UserProfile, record: record_models.EncryptedRecord, aes_key: str) -> None:
        """
        add encryption key of record for user
        :param user: new encryption key holder
        :param record: record where key gets added for user
        :param aes_key: aes key of record
        :return:
        """
        pub = user.get_public_key()
        encrypted_key = RSAEncryption.encrypt(aes_key, pub)
        record_encryption = record_models.RecordEncryption(user=user, record=record, encrypted_key=encrypted_key)
        record_encryption.save()
