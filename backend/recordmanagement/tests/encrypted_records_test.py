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

from django.test import TransactionTestCase

from backend.api.models import UserProfile, Permission
from backend.api.tests.statics import StaticTestMethods
from backend.recordmanagement.models import EncryptedRecord, EncryptedRecordPermission
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC


class EncryptedRecordTests(TransactionTestCase):
    def setUp(self):
        self.client = StaticTestMethods.force_authentication()
        self.base_list_url = '/api/records/records/'
        self.base_detail_url = '/api/records/record/'
        self.base_create_record_url = '/api/records/create_record/'

    def test_user_has_permission(self):
        user1 = UserProfile(email='abc1@web.de', name="abc1")
        user1.save()
        user2 = UserProfile(email='abc2@web.de', name="abc2")
        user2.save()
        user3 = UserProfile(email='abc3@web.de', name="abc3")
        user3.save()
        record = EncryptedRecord(record_token='asd123')
        record.save()
        record.working_on_record.add(user1)

        permission = EncryptedRecordPermission(request_from=user2, request_processed=user3, state='gr', record=record)
        permission.save()

        self.assertTrue(record.user_has_permission(user1))
        self.assertTrue(record.user_has_permission(user2))

    def test_get_users_with_permission(self):
        # get_users_with_permission needs permission in database
        permission = Permission(name=PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC)
        permission.save()

        user1 = UserProfile(email='abc1@web.de', name="abc1")
        user1.save()
        user2 = UserProfile(email='abc2@web.de', name="abc2")
        user2.save()
        user3 = UserProfile(email='abc3@web.de', name="abc3")
        user3.save()
        record = EncryptedRecord(record_token='asd123')
        record.save()
        record.working_on_record.add(user1)

        permission = EncryptedRecordPermission(request_from=user2, request_processed=user3, state='gr', record=record)
        permission.save()

        users_with_permission = record.get_users_with_permission()
        self.assertTrue(users_with_permission.__len__() == 2)
        self.assertTrue(user1 in users_with_permission)
        self.assertTrue(user2 in users_with_permission)
