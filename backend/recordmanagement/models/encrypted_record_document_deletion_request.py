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
from backend.api.models import UserProfile
from django.utils import timezone


class EncryptedRecordDocumentDeletionRequest(models.Model):
    document = models.ForeignKey(
        "EncryptedRecordDocument",
        related_name="deletion_requests",
        on_delete=models.SET_NULL,
        null=True,
    )
    record = models.ForeignKey(
        "EncryptedRecord",
        related_name="document_deletions_requests",
        on_delete=models.SET_NULL,
        null=True,
    )

    request_from = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    request_processed = models.ForeignKey(
        UserProfile,
        related_name="record_document_deletion_requests_processed",
        on_delete=models.SET_NULL,
        null=True,
    )
    explanation = models.TextField(default="")
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

    def __str__(self) -> str:
        return "record document deletion request: " + str(self.id)
