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
from backend.static.storage_folders import get_storage_folder_record_document


class RecordDocument(models.Model):
    name = models.CharField(max_length=200, unique=True)
    creator = models.ForeignKey(
        UserProfile, related_name="record_documents_created", on_delete=models.SET_NULL, null=True)

    record = models.ForeignKey('Record', related_name="record_documents", on_delete=models.CASCADE,
                               null=True, default=None)

    created_on = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    file_size = models.BigIntegerField()

    tagged = models.ManyToManyField('RecordDocumentTag', related_name="tagged", blank=True)

    def __str__(self):
        return 'record_document: ' + str(self.id) + ':' + self.name

    def get_filekey(self):
        return get_storage_folder_record_document(self.record.from_rlc_id, self.record.id) + self.name
