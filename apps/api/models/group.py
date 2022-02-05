from apps.api.models.has_permission import HasPermission
from apps.api.models.permission import Permission
from apps.api.models.user import UserProfile
from apps.static import permissions
from django.db import models


class GroupQuerySet(models.QuerySet):
    def get_visible_groups_for_user(self, user):
        if user.has_permission(permissions.PERMISSION_MANAGE_GROUPS_RLC):
            return self.filter(from_rlc=user.rlc)
        return self.filter(from_rlc=user.rlc, visible=True)


class Group(models.Model):
    creator = models.ForeignKey(UserProfile, related_name="group_created", on_delete=models.SET_NULL, null=True)
    from_rlc = models.ForeignKey("Rlc", related_name="group_from_rlc", on_delete=models.SET_NULL, null=True,
                                 default=None)
    name = models.CharField(max_length=200, null=False)
    visible = models.BooleanField(null=False, default=True)
    group_members = models.ManyToManyField(UserProfile, related_name="rlcgroups", blank=True)
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    objects = GroupQuerySet.as_manager()

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return "group: {}; name: {}; rlc: {};".format(self.id, self.name, self.from_rlc.name)
