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
from django.db import models
from django.db.models import Q
from datetime import datetime
import pytz
from django_prometheus.models import ExportModelOperationsMixin
from django.utils import timezone

from backend.api.errors import CustomError
from backend.api.models import Rlc, UserProfile, UserActivityPath
from backend.recordmanagement.models import RecordTag
from backend.static import error_codes
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC
from backend.static.date_utils import parse_date
from backend.static.encryption import AESEncryption
from backend.static import permissions


class UserActivity(models.Model):
    user = models.CharField(max_length=255, null=False)
    rlc = models.ForeignKey(
        Rlc,
        related_name="user_activity",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    time = models.DateTimeField(default=timezone.now)
    path = models.ForeignKey(
        UserActivityPath,
        related_name="user_activity",
        on_delete=models.SET_NULL,
        null=True,
    )
