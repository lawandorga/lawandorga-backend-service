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

from django.db import models

from backend.api.models import UserProfile
from backend.static.string_generator import get_random_string


def generate_link_id():
    length = 32
    pot_id = get_random_string(length)
    while True:
        try:
            UserActivationLink.objects.get(link=pot_id)
            pot_id = get_random_string(length)
        except:
            return pot_id


class UserActivationLink(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    link = models.CharField(auto_created=True, unique=True, default=generate_link_id, max_length=32)
    date = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)

    def __str__(self):
        return 'user activation link: ' + str(self.id) + ':' + self.user.email
