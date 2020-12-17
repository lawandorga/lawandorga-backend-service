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
from backend.collab.models import TextDocument


class TextDocumentVersion(
    ExportModelOperationsMixin("text_document_version"), models.Model
):
    document = models.ForeignKey(
        TextDocument, related_name="versions", null=False, on_delete=models.CASCADE
    )
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(
        UserProfile,
        related_name="text_document_versions_created",
        on_delete=models.SET_NULL,
        null=True,
    )

    is_draft = models.BooleanField(default=True)
    content = models.BinaryField()
