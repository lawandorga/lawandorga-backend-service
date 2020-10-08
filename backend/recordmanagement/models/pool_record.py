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
from django_prometheus.models import ExportModelOperationsMixin

from backend.api.models import UserProfile
from backend.recordmanagement.models import EncryptedRecord


class PoolRecord(ExportModelOperationsMixin("pool_record"), models.Model):
    record = models.ForeignKey(
        EncryptedRecord,
        related_name="e_record_pool_entry",
        on_delete=models.CASCADE,
        null=False,
    )
    enlisted = models.DateTimeField(auto_now_add=True)
    yielder = models.ForeignKey(
        UserProfile,
        related_name="e_records_yielded",
        on_delete=models.SET_NULL,
        null=True,
    )
    record_key = models.CharField(null=False, max_length=255)
