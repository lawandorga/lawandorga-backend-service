from django.db import models


class CollabPermission(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        verbose_name = "CollabPermission"
        verbose_name_plural = "CollabPermissions"

    def __str__(self):
        return "collabPermission: {}; name: {};".format(self.pk, self.name)
