from apps.api.models.permission import Permission
from django.db import models


class HasPermission(models.Model):
    permission = models.ForeignKey(Permission, related_name="in_has_permission", on_delete=models.CASCADE)
    user_has_permission = models.ForeignKey("UserProfile", related_name="user_has_permission", blank=True,
                                            on_delete=models.CASCADE, null=True)
    group_has_permission = models.ForeignKey("Group", related_name="group_has_permission", blank=True,
                                             on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "HasPermission"
        verbose_name_plural = "HasPermissions"

    def __str__(self):
        return "hasPermission: {}; name: {};".format(self.pk, self.permission.name)
