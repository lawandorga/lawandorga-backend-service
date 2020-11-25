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
from model_utils.managers import InheritanceManager
from django_prometheus.models import ExportModelOperationsMixin

from backend.api.models import Rlc, UserProfile


class TextDocument(ExportModelOperationsMixin("text_document"), models.Model):
    rlc = models.ForeignKey(
        Rlc, related_name="text_documents", null=False, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, null=False)

    content = models.BinaryField()

    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(
        UserProfile,
        related_name="text_documents_created",
        on_delete=models.SET_NULL,
        null=True,
    )
    last_edited = models.DateTimeField(default=timezone.now)
    last_editor = models.ForeignKey(
        UserProfile,
        related_name="text_documents_last_updated",
        on_delete=models.SET_NULL,
        null=True,
    )

    objects = InheritanceManager()
