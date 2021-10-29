from typing import Dict, Tuple
from django.db import models
from apps.api.errors import CustomError
from apps.api.models import UserProfile
from apps.collab.models import TextDocument
from apps.collab.static.collab_permissions import (
    PERMISSION_READ_DOCUMENT,
    PERMISSION_WRITE_DOCUMENT,
)
from apps.static.permissions import (
    PERMISSION_MANAGE_COLLAB_DOCUMENT_PERMISSIONS_RLC,
    PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC,
    PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC,
)


class CollabDocument(TextDocument):
    path = models.CharField(max_length=4096, null=False, blank=False)

    @property
    def name(self):
        return self.path.split('/')[-1]

    @property
    def root(self):
        return self.path[1:].count('/') == 0

    def save(self, *args, **kwargs) -> None:
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
        from apps.collab.models import PermissionForCollabDocument

        groups = user.rlcgroups.all()

        permissions_direct = PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups, document__path=self.path
        )
        permissions_all = PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups, document__path__startswith=self.path
        )
        return permissions_all.count() > 0, permissions_direct.count() > 0

    @staticmethod
    def user_has_permission_read(path: str, user: UserProfile) -> bool:
        from apps.collab.models import PermissionForCollabDocument

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
        groups = user.rlcgroups.all()
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
        from apps.collab.models import PermissionForCollabDocument

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

        groups = user.rlcgroups.all()
        if PermissionForCollabDocument.objects.filter(
            permission__name=PERMISSION_WRITE_DOCUMENT,
            document__path__in=parents,
            group_has_permission__in=groups,
        ).exists():
            return True
        return False
