#  rlcapp - record and organization management software for refugee law clinics
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

from django.test import TransactionTestCase
from backend.static.regex_validators import is_storage_folder_of_record, is_phone_number


class RegexTests(TransactionTestCase):
    def setUp(self):
        pass

    def test_array(self, values, method_to_check):
        for value in values:
            b = method_to_check(value)
            a = 10
            self.assertTrue(method_to_check(value))

    def test_is_storage_folder_success(self):
        folder = 'rlcs/123/records/123/'
        self.assertTrue(is_storage_folder_of_record(folder))
        folder = 'rlcs/123/records/123'
        self.assertTrue(is_storage_folder_of_record(folder))

    def test_is_storage_folder_error(self):
        folder = 'aa/123/records/123/'
        self.assertTrue(not is_storage_folder_of_record(folder))
        folder = 'rlcs/123a/records/123/'
        self.assertTrue(not is_storage_folder_of_record(folder))

    def test_is_phone_number_success(self):
        numbers = [
            '0753939209',
            '07539 39209',
            '08923738',
            # '07539-39209',
            # '07539/39209'
        ]
        self.test_array(numbers, is_phone_number)






