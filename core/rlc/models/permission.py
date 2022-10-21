from django.db import models


class Permission(models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)
    description = models.TextField(blank=True)
    recommended_for = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ["name"]

    def __str__(self):
        return "permission: {}; name: {};".format(self.pk, self.name)
