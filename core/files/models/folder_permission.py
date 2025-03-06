from django.db import models


class FolderPermission(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        verbose_name = "FIL_FolderPermission"
        verbose_name_plural = "FIL_FolderPermissions"

    def __str__(self):
        return "folderPermission: {}; name: {};".format(self.pk, self.name)
