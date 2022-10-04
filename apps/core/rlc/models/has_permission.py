from django.db import models

from .permission import Permission


class HasPermission(models.Model):
    permission = models.ForeignKey(
        Permission, related_name="in_has_permission", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "RlcUser",
        related_name="permissions",
        blank=True,
        on_delete=models.CASCADE,
        null=True,
    )
    group_has_permission = models.ForeignKey(
        "Group",
        related_name="group_has_permission",
        blank=True,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = "HasPermission"
        verbose_name_plural = "HasPermissions"
        unique_together = ("permission", "user", "group_has_permission")

    def __str__(self):
        return "hasPermission: {}; name: {};".format(self.pk, self.permission.name)
