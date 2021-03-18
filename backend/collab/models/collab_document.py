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
from typing import Optional, Sequence, Union

from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from backend.collab.models import TextDocument
from backend.api.models import Rlc


class CollabDocument(ExportModelOperationsMixin("collab_document"), TextDocument):
    path = models.CharField(max_length=4096, null=False, blank=False)

    def save(self, *args, **kwargs) -> None:
        if "/" in self.path:
            parent_doc = "/".join(self.path.split("/")[0:-1])
            if not CollabDocument.objects.filter(path=parent_doc).exists():
                raise ValueError("parent document doesn't exist")

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

        # if "/" in self.name:
        #     raise ValueError("CollabDocument name can't contain a /")
        # # if CollabDocument.objects.filter()
        #
        # if not CollabDocument.objects.filter(name=self.name, path=self.path).exists():
        #     return super().save(*args, **kwargs)
        # # it's a duplicate (name and path), append number at the end and save
        # count = 1
        # org_name = self.name
        # while True:
        #     new_name = "{}({})".format(org_name, count)
        #     if CollabDocument.objects.filter(name=new_name, path=self.path).exists():
        #         count += 1
        #         continue
        #     else:
        #         self.name = new_name
        #         return super().save(*args, **kwargs)

    @staticmethod
    def create_or_duplicate(collab_document: "CollabDocument") -> "CollabDocument":
        """
        TODO: delete, deprecated
        creates new collab document, either with given name
        or if name under parent doc is already exsiting with appendix (1), (2)...
        :param collab_document:
        :return:
        """
        try:
            CollabDocument.objects.get(
                parent=collab_document.parent, name=collab_document.name
            )
        except:
            collab_document.save()
            return collab_document
        count = 1
        while True:
            new_name = collab_document.name + " (" + str(count) + ")"
            try:
                CollabDocument.objects.get(parent=collab_document.parent, name=new_name)
                count += 1
            except:
                collab_document.name = new_name
                collab_document.save()
                return collab_document

    @staticmethod
    def get_collab_document_from_path(path: str, rlc: Rlc) -> "CollabDocument":
        """
        TODO: check if and where really needed, delete or refactor
        searches for collab document in virtual path
        a document can have child_pages / a parent page -> parent is above in folder
        pages in paths are separated through "//"
        :param path:
        :param rlc:
        :return:
        """
        path_parts = path.split("//")
        i = 0

        collab_doc = CollabDocument.objects.filter(
            name=path_parts[i], parent=None, rlc=rlc
        ).first()
        if not collab_doc:
            return None
        while True:
            i += 1
            if i >= path_parts.__len__() or path_parts[i] == "":
                break
            if not collab_doc:
                # ERROR
                pass
            collab_doc = collab_doc.child_pages.filter(name=path_parts[i]).first()
        return collab_doc
