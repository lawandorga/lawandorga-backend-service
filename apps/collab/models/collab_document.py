from apps.collab.static.collab_permissions import PERMISSION_WRITE_DOCUMENT
from apps.static.permissions import PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC, PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC
from apps.api.models import Rlc, UserProfile
from django.utils import timezone
from django.db import models
from typing import Dict, Tuple


class CollabDocument(models.Model):
    # textdocument_ptr = models.OneToOneField(auto_created=True, on_delete=models.CASCADE, null=False,
    #                                         parent_link=True, to=TextDocument, primary_key=False)
    # id = models.IntegerField(primary_key=True)
    rlc = models.ForeignKey(Rlc, related_name="collab_documents", null=True, on_delete=models.CASCADE, blank=True)
    created = models.DateTimeField(null=True) #default=timezone.now)
    creator = models.ForeignKey(UserProfile, related_name="collab_documents", on_delete=models.SET_NULL,
                                    null=True)
    # rlc = models.ForeignKey(Rlc, related_name="text_documents", null=True, on_delete=models.CASCADE, blank=True)
    # created = models.DateTimeField(auto_created=True)
    # updated = models.DateTimeField(auto_now=True)
    # creator = models.ForeignKey(UserProfile, related_name="text_documents_created", on_delete=models.SET_NULL,
    #                             null=True, blank=True)
    path = models.CharField(max_length=4096, null=False, blank=False)

    class Meta:
        verbose_name = 'CollabDocument'
        verbose_name_plural = 'CollabDocuments'

    def __str__(self):
        return 'collabDocument: {}; name: {};'.format(self.pk, self.name)

    @property
    def name(self):
        return self.path.split('/')[-1]

    @property
    def root(self):
        return self.path[1:].count('/') == 0

    def save(self, *args, **kwargs) -> None:
        if CollabDocument.objects.exclude(pk=self.pk).filter(path=self.path).exists():
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
        CollabDocument.objects.exclude(path=self.path).filter(path__startswith="{}/".format(self.path)).delete()
        return super().delete(*args, **kwargs)

    def user_can_read(self, user):
        if (
            user.has_permission(PERMISSION_READ_ALL_COLLAB_DOCUMENTS_RLC)
            or user.has_permission(PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC)
        ):
            return True

        permissions = list(user.get_collab_permissions())

        for permission in permissions:
            permission_path = permission.document.path
            if self.path.startswith(permission_path) and self.path.count('/') > permission_path.count('/'):
                # this means the user has permission to write on a parent path
                return True
            if self.path == permission_path:
                # this means the user has permission for exactly this document
                return True

        return False

    def user_can_write(self, user):
        if user.has_permission(PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC):
            return True

        permissions = list(user.get_collab_permissions().filter(permission__name=PERMISSION_WRITE_DOCUMENT))

        for permission in permissions:
            permission_path = permission.document.path
            if self.has_permission_direct(permission_path) or self.has_permission_from_parent(permission_path):
                return True

        return False

    @staticmethod
    def user_has_permission_write(path, user):
        if user.has_permission(PERMISSION_WRITE_ALL_COLLAB_DOCUMENTS_RLC):
            return True

        permissions = list(user.get_collab_permissions().filter(permission__name=PERMISSION_WRITE_DOCUMENT))

        for permission in permissions:
            permission_path = permission.document.path
            if path.startswith(permission_path) and path.count('/') > permission_path.count('/'):
                # this means the user has permission to write on a parent path
                return True
            if path == permission_path:
                # this means the user has permission for exactly this document
                return True

        return False

    def has_permission_from_parent(self, permission_path):
        return self.path.startswith(permission_path) and self.path.count('/') > permission_path.count('/')

    def has_permission_direct(self, permission_path):
        return self.path == permission_path

    def has_permission_from_below(self, permission_path):
        return permission_path.startswith(self.path) and self.path.count('/') < permission_path.count('/')
