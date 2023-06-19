from typing import TYPE_CHECKING, Union

from django.db import models

if TYPE_CHECKING:
    from core.auth.models.org_user import RlcUser
    from core.rlc.models.group import Group


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


class HasPermission(models.Model):
    @classmethod
    def create(
        cls,
        permission: Permission,
        user: Union["RlcUser", None] = None,
        group: Union["Group", None] = None,
    ):
        assert user or group
        assert not (user and group)
        has_permission = cls(
            permission=permission, user=user, group_has_permission=group
        )
        return has_permission

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

    @property
    def permission_name(self):
        return self.permission.name

    @property
    def user_name(self):
        if self.user:
            return self.user.name
        return None

    @property
    def group_name(self):
        if self.group_has_permission:
            return self.group_has_permission.name
        return None

    @property
    def group_id(self):
        if self.group_has_permission_id:
            return self.group_has_permission_id
        return None

    # @property
    # def user_id(self):
    #     if self.user_id:
    #         return self.user_id
    #     return None

    @property
    def source(self):
        if self.user and not self.group_has_permission:
            return "USER"
        if not self.user and self.group_has_permission:
            return "GROUP"
        raise ValueError("No valid source on this permission.")
