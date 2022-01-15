from apps.api.models.permission import Permission
from django.db import models


class HasPermission(models.Model):
    permission = models.ForeignKey(
        Permission,
        related_name="in_has_permission",
        null=False,
        on_delete=models.CASCADE,
    )
    user_has_permission = models.ForeignKey(
        "UserProfile",
        related_name="user_has_permission",
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

    def __str__(self):
        return "hasPermission: {}; name: {};".format(self.pk, self.permission.name)

    @staticmethod
    def already_existing(data):
        entries = HasPermission.objects.filter(
            permission=data.get("permission", None),
            user_has_permission=data.get("user_has_permission", None),
            group_has_permission=data.get("group_has_permission", None),
        ).count()
        if entries == 0:
            return False
        return True

    """
    check if values which are in data can made to a valid get_as_user_permissions
    :returns True, if valid, False if invalid
    """
    @staticmethod
    def validate_values(data):
        if (
            HasPermission._check_key_with_value_in_data(data, "user_has_permission")
            + HasPermission._check_key_with_value_in_data(data, "group_has_permission")
            == 1
        ):
            return True
        return False

    """
    Checks if the key key is in the dict data and if it has a value other than '' and none
    :returns 0 if not there, '' or none, 1 if other
    """
    @staticmethod
    def _check_key_with_value_in_data(data, key):
        return int(key in data and data[key] != "" and data[key] is not None)
