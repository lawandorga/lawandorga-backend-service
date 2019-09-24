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
from backend.api.models.user import phone_regex
from backend.api.models import Rlc


class Client(models.Model):
    from_rlc = models.ForeignKey(Rlc, related_name='client_from_rlc', on_delete=models.SET_NULL, null=True)
    created_on = models.DateField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=200)
    note = models.TextField(max_length=4096, null=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=100, null=True, default=None)

    birthday = models.DateField(null=True, blank=True)
    origin_country = models.ForeignKey('OriginCountry', related_name='clients', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return 'client: ' + str(self.id) + ':' + self.name
