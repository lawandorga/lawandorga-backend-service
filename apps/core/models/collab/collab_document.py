from django.db import models

from apps.core.models.rlc import Rlc
from apps.core.static import (
    PERMISSION_COLLAB_READ_ALL_DOCUMENTS,
    PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS,
    PERMISSION_WRITE_DOCUMENT,
)


class CollabDocument(models.Model):
    rlc = models.ForeignKey(
        Rlc, related_name="collab_documents", on_delete=models.CASCADE, blank=True
    )
    path = models.CharField(max_length=4096, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CollabDocument"
        verbose_name_plural = "CollabDocuments"
        unique_together = ("rlc", "path")
        ordering = ["path"]

    def __str__(self):
        return "collabDocument: {}; name: {};".format(self.pk, self.name)

    @property
    def name(self):
        return self.path.split("/")[-1]

    @property
    def root(self):
        return self.path[1:].count("/") == 0

    def change_name_and_save(self, new_name):
        old_path = self.path
        new_path = "{}/{}".format("/".join(self.path.split("/")[:-1]), new_name)
        for doc in CollabDocument.objects.filter(path__startswith=old_path):
            doc.path = doc.path.replace(old_path, new_path)
            doc.save()
        return CollabDocument.objects.get(pk=self.pk)

    def delete(self, *args, **kwargs):
        path = "{}/".format(self.path)
        CollabDocument.objects.exclude(path=self.path).filter(
            path__startswith=path, rlc=self.rlc
        ).delete()
        return super().delete(*args, **kwargs)

    def user_can_read(self, user):
        if user.has_permission(
            PERMISSION_COLLAB_READ_ALL_DOCUMENTS
        ) or user.has_permission(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS):
            return True

        permissions = list(user.get_collab_permissions())

        for permission in permissions:
            permission_path = permission.document.path
            if self.path.startswith(permission_path) and self.path.count(
                "/"
            ) > permission_path.count("/"):
                # this means the user has permission to write on a parent path
                return True
            if self.path == permission_path:
                # this means the user has permission for exactly this document
                return True

        return False

    def user_can_write(self, user):
        if user.has_permission(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS):
            return True

        permissions = list(
            user.get_collab_permissions().filter(
                permission__name=PERMISSION_WRITE_DOCUMENT
            )
        )

        for permission in permissions:
            permission_path = permission.document.path
            if self.has_permission_direct(
                permission_path
            ) or self.has_permission_from_parent(permission_path):
                return True

        return False

    @staticmethod
    def user_has_permission_write(path, user):
        if user.has_permission(PERMISSION_COLLAB_WRITE_ALL_DOCUMENTS):
            return True

        permissions = list(
            user.get_collab_permissions().filter(
                permission__name=PERMISSION_WRITE_DOCUMENT
            )
        )

        for permission in permissions:
            permission_path = permission.document.path
            if path.startswith(permission_path) and path.count(
                "/"
            ) > permission_path.count("/"):
                # this means the user has permission to write on a parent path
                return True
            if path == permission_path:
                # this means the user has permission for exactly this document
                return True

        return False

    def has_permission_from_parent(self, permission_path):
        return self.path.startswith(permission_path) and self.path.count(
            "/"
        ) > permission_path.count("/")

    def has_permission_direct(self, permission_path):
        return self.path == permission_path

    def has_permission_from_below(self, permission_path):
        return permission_path.startswith(self.path) and self.path.count(
            "/"
        ) < permission_path.count("/")
