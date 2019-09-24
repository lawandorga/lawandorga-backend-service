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


class RecordMessage(models.Model):
    sender = models.ForeignKey(
        UserProfile, related_name="record_messages_sent", on_delete=models.SET_NULL, null=True)

    record = models.ForeignKey('Record', related_name="record_messages", on_delete=models.CASCADE,
                               null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=4096, null=False)

    def __str__(self):
        return 'record_message: ' + str(self.id) + '; message: ' + self.message
