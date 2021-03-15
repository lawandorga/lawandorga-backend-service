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

from backend.collab.models import (
    CollabPermission,
    PermissionForCollabDocument,
    TextDocument,
)
from backend.api.models import Rlc, UserProfile


class CollabDocument(ExportModelOperationsMixin("collab_document"), TextDocument):
    parent = models.ForeignKey(
        "CollabDocument",
        related_name="child_pages",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )

    def user_can_view(self, user: UserProfile) -> bool:
        user_groups = user.group_members.all()
        permissions = CollabPermission.objects.all()

        return self.user_can_view_recursive(user, user_groups, permissions)

    def user_can_view_recursive(self, user, groups, permissions):
        if PermissionForCollabDocument.objects.exists(
            document=self, group_has_permission__in=groups, permission__in=permissions,
        ):
            return True
        for child in self.child_pages:
            if child.user_can_view(user):
                return True
        return False

    @staticmethod
    def create_or_duplicate(collab_document: "CollabDocument") -> "CollabDocument":
        """
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
