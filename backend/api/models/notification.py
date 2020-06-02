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

from enum import Enum
from django.db import models

from backend.api.models import UserProfile


class NotificationTypes(Enum):
    RECORD = 1
    RECORD_MESSAGE = 2


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, related_name="notifications", on_delete=models.CASCADE)
    message = models.CharField(max_length=2048)
    source_user = models.ForeignKey(UserProfile, related_name="notification_caused", on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=1024)
    ref_id = models.CharField(max_length=50)


