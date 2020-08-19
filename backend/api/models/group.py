#  law&orga - record and organization management software for refugee law clinics
#  Copyright (C) 2019  Dominik Walser
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>
from django.db import models
from django.db.models import Q

from backend.static import permissions
from . import UserProfile


class GroupQuerySet(models.QuerySet):
    def get_visible_groups_for_user(self, user):
        from backend.api.models import Group

        if user.has_permission(
            permissions.PERMISSION_MANAGE_GROUPS_RLC, for_rlc=user.rlc
        ):
            return self.filter(from_rlc=user.rlc)
        else:
            invisible = list(Group.objects.filter(from_rlc=user.rlc, visible=False))
            permitted = []
            for gr in invisible:
                if user.has_permission(
                    permissions.PERMISSION_MANAGE_GROUP, for_group=gr
                ):
                    permitted.append(gr.id)

            return self.filter(Q(from_rlc=user.rlc, visible=True) | Q(id__in=permitted))


class Group(models.Model):
    creator = models.ForeignKey(
        UserProfile, related_name="group_created", on_delete=models.SET_NULL, null=True
    )
    from_rlc = models.ForeignKey(
        "Rlc",
        related_name="group_from_rlc",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )
    name = models.CharField(max_length=200, null=False)
    visible = models.BooleanField(null=False, default=True)
    group_members = models.ManyToManyField(UserProfile, related_name="group_members")
    description = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    objects = GroupQuerySet.as_manager()

    def __str__(self):
        return (
            "group: " + str(self.id) + ":" + self.name + "; from " + str(self.from_rlc)
        )

    def has_group_permission(self, permission):
        from backend.api.models import HasPermission, Permission

        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission)
        return (
            HasPermission.objects.filter(
                group_has_permission=self,
                permission_for_rlc=self.from_rlc,
                permission=permission,
            ).count()
            >= 1
        )

    def has_group_one_permission(self, permissions_to_check):
        for permission in permissions_to_check:
            if self.has_group_permission(permission):
                return True
        return False

    def group_has_record_encryption_keys_permission(self):
        record_encryption_keys_permissions = (
            permissions.get_record_encryption_keys_permissions()
        )
        return self.has_group_one_permission(record_encryption_keys_permissions)
