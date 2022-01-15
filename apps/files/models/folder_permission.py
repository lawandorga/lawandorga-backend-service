from django.db import models


class FolderPermission(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        verbose_name = "FolderPermission"
        verbose_name_plural = "FolderPermissions"

    def __str__(self):
        return "folderPermission: {}; name: {};".format(self.pk, self.name)
