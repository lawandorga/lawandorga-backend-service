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
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

from backend.api.models import UserProfile


class EncryptedRecordDeletionRequest(
    ExportModelOperationsMixin("encrypted_record_deletion_request"), models.Model
):
    record = models.ForeignKey(
        "EncryptedRecord",
        related_name="deletions_requested",
        on_delete=models.SET_NULL,
        null=True,
    )
    request_from = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    request_processed = models.ForeignKey(
        UserProfile,
        related_name="e_record_deletion_request_processed",
        on_delete=models.SET_NULL,
        null=True,
    )
    explanation = models.CharField(max_length=4096, default="")
    requested = models.DateTimeField(default=timezone.now)
    processed_on = models.DateTimeField(null=True)

    record_deletion_request_states_possible = (
        ("re", "requested"),
        ("gr", "granted"),
        ("de", "declined"),
    )
    state = models.CharField(
        max_length=2, choices=record_deletion_request_states_possible, default="re"
    )

    def __str__(self):
        return "e record deletion request:" + str(self.id)
