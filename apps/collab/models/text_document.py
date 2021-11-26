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
from apps.api.models import Rlc, UserProfile
from apps.api.errors import CustomError
from apps.static.error_codes import (
    ERROR__COLLAB__TYPE_NOT_EXISTING,
    ERROR__NOT__IMPLEMENTEND,
)


class TextDocument(models.Model):
    rlc = models.ForeignKey(Rlc, related_name="text_documents", null=False, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(
        UserProfile,
        related_name="text_documents_created",
        on_delete=models.SET_NULL,
        null=True,
    )

    objects = InheritanceManager()

    def get_collab_document(self) -> "CollabDocument":
        try:
            collab_doc = self.collabdocument
            return collab_doc
        except Exception as e:
            raise CustomError(ERROR__COLLAB__TYPE_NOT_EXISTING)

    def get_record_document(self) -> "RecordDocument":
        try:
            record_doc = self.recorddocument
            return record_doc
        except Exception as e:
            raise CustomError(ERROR__COLLAB__TYPE_NOT_EXISTING)

    def patch(self, document_data: {}, user: UserProfile) -> None:
        # TODO: recheck this
        if "content" in document_data or "name" in document_data:
            if "name" in document_data:
                self.name = document_data["name"]
            self.last_editor = user
            self.last_edited = timezone.now()
            self.save()

    def get_last_published_version(self) -> "TextDocumentVersion":
        return self.versions.filter(is_draft=False).order_by("-created").first()

    def get_draft(self) -> "TextDocumentVersion":
        return self.versions.filter(is_draft=True).first()
