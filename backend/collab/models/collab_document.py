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
from typing import Any, Dict, Tuple

from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from backend.api.errors import CustomError
from backend.api.models import UserProfile
from backend.collab.models import TextDocument
from backend.collab.static.collab_permissions import (
    PERMISSION_READ_DOCUMENT,
    PERMISSION_WRITE_DOCUMENT,
)
from backend.static.permissions import (
    PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
    PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
    PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
)


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

    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:
        CollabDocument.objects.exclude(path=self.path).filter(
            path__startswith="{}/".format(self.path)
        ).delete()
        return super().delete(*args, **kwargs)

    def user_can_see(self, user: UserProfile) -> Tuple[int, int]:
        """
        checks if user is able to see this document
        return tuple with 2 elements
            first if visible at all
            second if visible directly (all subfolders should be visible too)
        :param user:
        :return:
        """
        from backend.collab.models import PermissionForCollabDocument

        groups = user.group_members.all()

        permissions_direct = PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups, document__path=self.path
        )
        permissions_all = PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups, document__path__startswith=self.path
        )
        return permissions_all.count() > 0, permissions_direct.count() > 0

    @staticmethod
    def user_has_permission_read(path: str, user: UserProfile) -> bool:
        from backend.collab.models import PermissionForCollabDocument

        if "/" not in path:
            return True

        overall_permissions_strings = [
            PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
            PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
            PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
        ]
        for permission in overall_permissions_strings:
            if user.has_permission(permission, for_rlc=user.rlc):
                return True

        parents = []
        parts = path.split("/")
        current = ""
        for part in parts:
            if current != "":
                current += "/"
            current += part
            parents.append(current)

        permission_names = [PERMISSION_READ_DOCUMENT, PERMISSION_WRITE_DOCUMENT]
        groups = user.group_members.all()
        for permission_name in permission_names:
            if PermissionForCollabDocument.objects.filter(
                permission__name=permission_name,
                document__path__in=parents,
                group_has_permission__in=groups,
            ).exists():
                return True
        return False

    @staticmethod
    def user_has_permission_write(path: str, user: UserProfile) -> bool:
        from backend.collab.models import PermissionForCollabDocument

        if "/" not in path:
            return True

        overall_permissions_strings = [
            PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
            PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
        ]
        for permission in overall_permissions_strings:
            if user.has_permission(permission, for_rlc=user.rlc):
                return True

        parents = []
        parts = path.split("/")
        current = ""
        for part in parts:
            if current != "":
                current += "/"
            current += part
            parents.append(current)

        groups = user.group_members.all()
        if PermissionForCollabDocument.objects.filter(
            permission__name=PERMISSION_WRITE_DOCUMENT,
            document__path__in=parents,
            group_has_permission__in=groups,
        ).exists():
            return True
        return False
