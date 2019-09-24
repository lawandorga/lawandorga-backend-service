#  rlcapp - record and organization management software for refugee law clinics
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
from django.db.models.query import QuerySet
from . import Permission


class HasPermissionQuerySet(QuerySet):
    def check_if_already_existing(self, val):
        return val


class HasPermissionManager(models.Manager):
    def get_query_set(self):
        return super().get_queryset()

    def __getattr__(self, item, *args):
        if item.startwith("_"):
            raise AttributeError
        return getattr(self.get_query_set(), item, *args)


class HasPermission(models.Model):
    permission = models.ForeignKey(Permission, related_name="in_has_permission", null=False,
                                   on_delete=models.CASCADE)
    user_has_permission = models.ForeignKey('UserProfile', related_name="user_has_permission",
                                            blank=True, on_delete=models.CASCADE, null=True)
    group_has_permission = models.ForeignKey('Group', related_name="group_has_permission",
                                             blank=True, on_delete=models.CASCADE, null=True)
    rlc_has_permission = models.ForeignKey('Rlc', related_name="rlc_has_permission",
                                           blank=True, on_delete=models.CASCADE, null=True)

    permission_for_user = models.ForeignKey('UserProfile', related_name="permission_for_user",
                                            blank=True, on_delete=models.CASCADE, null=True)
    permission_for_group = models.ForeignKey('Group', related_name="permission_for_group",
                                             blank=True, on_delete=models.CASCADE, null=True)
    permission_for_rlc = models.ForeignKey('Rlc', related_name="permission_for_rlc",
                                           blank=True, on_delete=models.CASCADE, null=True)

    objects = HasPermissionManager

    def __str__(self):
        return 'hasPermission: ' + str(self.id) + '; permissionName: ' + self.permission.name

    """
    
    """

    @staticmethod
    def already_existing(data):
        entries = HasPermission.objects.filter(
            permission=data.get('permission', None),
            user_has_permission=data.get('user_has_permission', None),
            group_has_permission=data.get('group_has_permission', None),
            rlc_has_permission=data.get('rlc_has_permission', None),
            permission_for_user=data.get('permission_for_user', None),
            permission_for_group=data.get('permission_for_group', None),
            permission_for_rlc=data.get('permission_for_rlc', None)
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
        if (HasPermission._check_key_with_value_in_data(data, 'user_has_permission') +
                HasPermission._check_key_with_value_in_data(data, 'group_has_permission') +
                HasPermission._check_key_with_value_in_data(data, 'rlc_has_permission') == 1 and
                HasPermission._check_key_with_value_in_data(data, 'permission_for_user') +
                HasPermission._check_key_with_value_in_data(data, 'permission_for_group') +
                HasPermission._check_key_with_value_in_data(data, 'permission_for_rlc') == 1):
            return True
        return False

    """
    Checks if the key key is in the dict data and if it has a value other than '' and none
    :returns 0 if not there, '' or none, 1 if other
    """

    @staticmethod
    def _check_key_with_value_in_data(data, key):
        return int(key in data and data[key] != '' and data[key] is not None)
