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
from backend.api.models import UserEncryptionKeys, UserProfile, Rlc, Group
from backend.static.encryption import RSAEncryption


class CreateFixtures:
    @staticmethod
    def create_fixtures():
        return_object = {}

        rlc = Rlc(name="testrlc", id=1)
        rlc.save()
        return_object.update({"rlc": rlc})

        users = []
        users.append(CreateFixtures.create_user(rlc, "user1"))
        users.append(CreateFixtures.create_user(rlc, "user2"))
        users.append(CreateFixtures.create_user(rlc, "user3"))
        users.append(CreateFixtures.create_user(rlc, "user4"))
        return_object.update({"users": users})

        groups = []
        groups.append(CreateFixtures.create_group(rlc, 'group1', [users[0]['user'], users[1]['user']]))
        groups.append(CreateFixtures.create_group(rlc, 'group2', [users[1]['user'], users[2]['user']]))
        return_object.update({'groups': groups})

        return return_object

    @staticmethod
    def create_user(rlc, name):
        user = UserProfile(name=name, email=name + "@law-orga.de", rlc=rlc)
        user.set_password("qwe123")
        user.save()
        private, public = RSAEncryption.generate_keys()
        keys = UserEncryptionKeys(user=user, private_key=private, public_key=public)
        keys.save()
        client = APIClient()
        client.force_authenticate(user=user)
        return {
            "user": user,
            "private": private,
            "client": client
        }

    @staticmethod
    def create_group(rlc, name, members):
        group = Group(name=name, from_rlc=rlc, visible=True)
        group.save()

        for member in members:
            group.group_members.add(member)
        return group
