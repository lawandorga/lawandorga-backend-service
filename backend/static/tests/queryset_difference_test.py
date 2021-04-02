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


from backend.api.models import UserProfile
from django.test import TransactionTestCase


class QuerysetDifferenceTest(TransactionTestCase):
    def setUp(self):
        user0: UserProfile = UserProfile(
            name="prop0 test0 user0", email="user0@test.com"
        )
        user0.save()
        user1: UserProfile = UserProfile(
            name="prop0 test1 user1", email="user1@test.com"
        )
        user1.save()
        user2: UserProfile = UserProfile(
            name="prop0 test2 user2", email="user2@test.com"
        )
        user2.save()

        user3: UserProfile = UserProfile(
            name="prop1 test0 user3", email="user3@test.com"
        )
        user3.save()
        user4: UserProfile = UserProfile(
            name="prop1 test1 user4", email="user4@test.com"
        )
        user4.save()
        user5: UserProfile = UserProfile(
            name="prop1 test2 user5", email="user5@test.com"
        )
        user5.save()

        user6: UserProfile = UserProfile(
            name="prop2 test0 user6", email="use6@test.com"
        )
        user6.save()
        user7: UserProfile = UserProfile(
            name="prop2 test1 user7", email="user7@test.com"
        )
        user7.save()
        user8: UserProfile = UserProfile(
            name="prop2 test2 user8", email="user8@test.com"
        )
        user8.save()
        self.users: [UserProfile] = [
            user0,
            user1,
            user2,
            user3,
            user4,
            user5,
            user6,
            user7,
            user8,
        ]
