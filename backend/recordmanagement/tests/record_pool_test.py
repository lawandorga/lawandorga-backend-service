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

from datetime import datetime
from django.test import TransactionTestCase
from rest_framework.test import APIClient

from backend.api.models import UserEncryptionKeys, UserProfile, Rlc, Permission, PERMISSION_CAN_CONSULT, HasPermission
from backend.recordmanagement.models import EncryptedRecord, PoolConsultant, PoolRecord, RecordEncryption
from backend.static.encryption import AESEncryption, RSAEncryption

PATH_POOL_RECORDS = '/api/records/pool_records/'
PATH_POOL_CONSULTANTS = '/api/records/pool_consultants/'
PATH_RECORD_POOL = '/api/records/record_pool/'


class RecordPoolTests(TransactionTestCase):
    def setUp(self):
        rlc = Rlc(name='testrlc')
        rlc.save()

        old_consultant = UserProfile(name="old consultant", email="old@law-orga.de", rlc=rlc)
        old_consultant.save()
        old_private, old_public = RSAEncryption.generate_keys()
        keys = UserEncryptionKeys(user=old_consultant, private_key=old_private, public_key=old_public)
        keys.save()
        self.old_consultant = old_consultant
        self.old_private = old_private
        client = APIClient()
        client.force_authenticate(user=old_consultant)
        self.old_client = client

        new_consultant = UserProfile(name='new consultant', email="new@law-orga.de", rlc=rlc)
        new_consultant.save()
        new_private, new_public = RSAEncryption.generate_keys()
        keys = UserEncryptionKeys(user=new_consultant, private_key=new_private, public_key=new_public)
        keys.save()
        self.new_consultant = new_consultant
        self.new_private = new_private
        new_client = APIClient()
        new_client.force_authenticate(user=new_consultant)
        self.new_client = new_client

        perm = Permission(name=PERMISSION_CAN_CONSULT)
        perm.save()
        has_perm = HasPermission(permission=perm, permission_for_rlc=rlc, rlc_has_permission=rlc)
        has_perm.save()

        record = EncryptedRecord(record_token='testrecord1', from_rlc=rlc)
        record.save()
        record.working_on_record.add(old_consultant)
        record.save()
        self.record = record
        record_key = AESEncryption.generate_secure_key()
        self.record_key = record_key
        encrypted_record_key = RSAEncryption.encrypt(record_key, old_public)
        record_encryption = RecordEncryption(user=old_consultant, record=record, encrypted_key=encrypted_record_key)
        record_encryption.save()

    def test_enlist_record_no_consultant_success(self):
        self.assertTrue(PoolRecord.objects.count() == 0)
        self.assertTrue(PoolConsultant.objects.count() == 0)

        to_post = {
            'record': self.record.id
        }
        response = self.old_client.post(PATH_POOL_RECORDS, data=to_post,
                                        **{'HTTP_PRIVATE_KEY': self.old_private})

        self.assertTrue(response.status_code == 200 or response.status_code == 201)
        self.assertTrue(response.data['action'] == 'created')
        self.assertTrue(PoolRecord.objects.count() == 1)
        self.assertTrue(PoolConsultant.objects.count() == 0)

    def test_enlist_record_no_consultant_no_record_provided(self):
        to_post = {
        }
        response = self.old_client.post(PATH_POOL_RECORDS, data=to_post,
                                        **{'HTTP_PRIVATE_KEY': self.old_private})

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data['error_code'] == 'api.id_not_provided')
        self.assertTrue(PoolRecord.objects.count() == 0)
        self.assertTrue(PoolConsultant.objects.count() == 0)

    def test_enlist_record_no_consultant_record_does_not_exist(self):
        to_post = {
            'record': self.record.id + 1
        }
        response = self.old_client.post(PATH_POOL_RECORDS, data=to_post,
                                        **{'HTTP_PRIVATE_KEY': self.old_private})

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data['error_code'] == 'record.record.not_existing')
        self.assertTrue(PoolRecord.objects.count() == 0)
        self.assertTrue(PoolConsultant.objects.count() == 0)

    def test_enlist_record_no_consultant_not_working_on(self):
        to_post = {
            'record': self.record.id
        }
        response = self.new_client.post(PATH_POOL_RECORDS, data=to_post,
                                        **{'HTTP_PRIVATE_KEY': self.new_private})

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data['error_code'] == 'record.permission.not_working_on')
        self.assertTrue(PoolRecord.objects.count() == 0)
        self.assertTrue(PoolConsultant.objects.count() == 0)

    def test_enlist_record_consultant_success(self):
        self.assertTrue(self.record.working_on_record.first() == self.old_consultant)
        pool_consultant = PoolConsultant(consultant=self.new_consultant, enlisted=datetime(2018, 4, 12, 18, 30, 0, 0))
        pool_consultant.save()
        pool_consultant = PoolConsultant(consultant=self.old_consultant, enlisted=datetime(2019, 4, 12, 18, 30, 0, 0))
        pool_consultant.save()



        to_post = {
            'record': self.record.id
        }
        response = self.old_client.post(PATH_POOL_RECORDS, data=to_post,
                                        **{'HTTP_PRIVATE_KEY': self.old_private})

        self.assertTrue(response.status_code == 200 or response.status_code == 201)
        self.assertTrue(PoolRecord.objects.count() == 0)
        self.assertTrue(PoolConsultant.objects.count() == 1)
        self.assertTrue(self.record.working_on_record.first() == self.new_consultant)
        self.assertTrue(RecordEncryption.objects.filter(record=self.record).first().user == self.new_consultant)
        self.assertTrue(RecordEncryption.objects.filter(record=self.record).count() == 1)
        self.assertTrue(response.data['action'] == 'matched')

    def test_enlist_consultant_no_records_success(self):
        self.assertTrue(PoolConsultant.objects.count() == 0)
        self.assertTrue(PoolRecord.objects.count() == 0)

        to_post = {
        }
        response = self.new_client.post(PATH_POOL_CONSULTANTS, data=to_post)

        self.assertTrue(response.status_code == 200 or response.status_code == 201)
        self.assertTrue(response.data['action'] == 'created')
        self.assertTrue(PoolConsultant.objects.count() == 1)
        self.assertTrue(PoolRecord.objects.count() == 0)

    def test_enlist_consultant_no_records_no_permission(self):
        HasPermission.objects.first().delete()
        self.assertTrue(PoolConsultant.objects.count() == 0)
        self.assertTrue(PoolRecord.objects.count() == 0)

        to_post = {
        }
        response = self.new_client.post(PATH_POOL_CONSULTANTS, data=to_post)

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data['error_code'] == 'api.permissions.insufficient')
        self.assertTrue(PoolConsultant.objects.count() == 0)
        self.assertTrue(PoolRecord.objects.count() == 0)

    def test_enlist_consultant_records_success(self):
        pool_record = PoolRecord(record=self.record, yielder=self.old_consultant, record_key=self.record_key)
        pool_record.save()

        self.assertTrue(PoolConsultant.objects.count() == 0)
        self.assertTrue(PoolRecord.objects.count() == 1)

        to_post = {
        }
        response = self.new_client.post(PATH_POOL_CONSULTANTS, data=to_post)

        self.assertTrue(response.status_code == 200 or response.status_code == 201)
        self.assertTrue(PoolConsultant.objects.count() == 0)
        self.assertTrue(PoolRecord.objects.count() == 0)
        self.assertTrue(self.record.working_on_record.first() == self.new_consultant)
        self.assertTrue(self.record.working_on_record.count() == 1)
        self.assertTrue(RecordEncryption.objects.filter(record=self.record).first().user == self.new_consultant)
        self.assertTrue(RecordEncryption.objects.filter(record=self.record).count() == 1)
        self.assertTrue(response.data['action'] == 'matched')

    def test_get_yielded_pool_records_success(self):
        pool_record = PoolRecord(record=self.record, yielder=self.old_consultant, record_key=self.record_key)
        pool_record.save()
        pool_record = PoolRecord(record=self.record, yielder=self.new_consultant, record_key=self.record_key)
        pool_record.save()

        response = self.new_client.get(PATH_RECORD_POOL)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.data) == 2)
        self.assertTrue(response.data['type'] == 'records')
        self.assertTrue(len(response.data['entries']) == 2)

    def test_get_enlisted_pool_consultants(self):
        pool_consultant = PoolConsultant(consultant=self.new_consultant, enlisted=datetime(2018, 4, 12, 18, 30, 0, 0))
        pool_consultant.save()

        response = self.new_client.get(PATH_RECORD_POOL)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.data) == 2)
        self.assertTrue(response.data['type'] == 'consultants')
        self.assertTrue(len(response.data['entries']) == 1)

    def test_get_empty_record_pool(self):
        response = self.new_client.get(PATH_RECORD_POOL)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data['type'] == 'empty')
