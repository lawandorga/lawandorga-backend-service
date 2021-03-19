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

from backend.api.errors import CustomError
from backend.collab.models import TextDocument


class CollabDocument(ExportModelOperationsMixin("collab_document"), TextDocument):
    path = models.CharField(max_length=4096, null=False, blank=False)

    def save(self, *args, **kwargs) -> None:
        if "/" in self.path:
            parent_doc = "/".join(self.path.split("/")[0:-1])
            if not CollabDocument.objects.filter(path=parent_doc).exists():
                # raise ValueError("parent document doesn't exist")
                raise CustomError("parent document doesn't exist")

        if CollabDocument.objects.filter(path=self.path).exists():
            count = 1
            org_path = self.path
            while True:
                new_path = "{}({})".format(org_path, count)
                if CollabDocument.objects.filter(path=new_path).exists():
                    count += 1
                    continue
                else:
                    self.path = new_path
                    return super().save(*args, **kwargs)

        return super().save(*args, **kwargs)
