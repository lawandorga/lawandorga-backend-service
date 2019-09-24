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

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from backend.api.errors import CustomError
from backend.static.error_codes import ERROR__API__PERMISSION__NOT_FOUND
from backend.static.regex_validators import phone_regex
from . import HasPermission, Permission


class UserProfileManager(BaseUserManager):
    """"""

    def create_user(self, email, name, password):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user

    @staticmethod
    def get_users_with_special_permission(permission, from_rlc=None, for_user=None, for_group=None, for_rlc=None):
        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission).id
        if for_user is not None and for_group is not None and for_rlc is not None:
            raise AttributeError()
        users = HasPermission.objects.filter(permission=permission,
                                             group_has_permission=None,
                                             rlc_has_permission=None,
                                             permission_for_user=for_user,
                                             permission_for_group=for_group,
                                             permission_for_rlc=for_rlc).values('user_has_permission').distinct()
        user_ids = [has_permission['user_has_permission'] for has_permission in users]
        result = UserProfile.objects.filter(id__in=user_ids).distinct()

        groups = HasPermission.objects.filter(permission=permission,
                                              user_has_permission=None,
                                              rlc_has_permission=None,
                                              permission_for_user=for_user,
                                              permission_for_group=for_group,
                                              permission_for_rlc=for_rlc).values('group_has_permission')
        group_ids = [has_permission['group_has_permission'] for has_permission in groups]
        result = result | UserProfile.objects.filter(group_members__in=group_ids).distinct()

        rlcs = HasPermission.objects.filter(permission=permission,
                                            user_has_permission=None,
                                            group_has_permission=None,
                                            permission_for_user=for_user,
                                            permission_for_group=for_group,
                                            permission_for_rlc=for_rlc).values('rlc_has_permission')
        rlc_ids = [has_permission['rlc_has_permission'] for has_permission in rlcs]
        result = result | UserProfile.objects.filter(rlc__in=rlc_ids).distinct()

        return result


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """ profile of users """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    birthday = models.DateField(null=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, null=True, default=None)

    # address
    street = models.CharField(max_length=255, default=None, null=True)
    city = models.CharField(max_length=255, default=None, null=True)
    postal_code = models.CharField(max_length=255, default=None, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    rlc = models.ForeignKey('Rlc', related_name='rlc_members', on_delete=models.SET_NULL, null=True)

    objects = UserProfileManager()

    user_states_possible = (
        ('ac', 'active'),
        ('ia', 'inactive'),
        ('ex', 'exam'),
        ('ab', 'abroad')
    )
    user_state = models.CharField(max_length=2, choices=user_states_possible)

    user_record_states_possible = (
        ('ac', 'accepting'),
        ('na', 'not accepting'),
        ('de', 'depends')
    )
    user_record_state = models.CharField(max_length=2, choices=user_record_states_possible)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # email already in there, other are default

    # class Meta:
    #     ordering = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return 'user: ' + str(self.id) + ':' + self.email

    def __get_as_user_permissions(self):
        """
        Returns: all HasPermissions the user itself has as list
        """
        return list(HasPermission.objects.filter(user_has_permission=self.pk))

    def __get_as_group_member_permissions(self):
        """
        Returns: all HasPermissions the groups in which the user is member of have as list
        """
        groups = [groups['id'] for groups in list(self.group_members.values('id'))]
        return list(HasPermission.objects.filter(group_has_permission_id__in=groups))

    def __get_as_rlc_member_permissions(self):
        """
        Returns: all HasPermissions the groups in which the user is member of have as list
        """
        return list(HasPermission.objects.filter(rlc_has_permission_id=self.rlc.id))

    def get_all_user_permissions(self):
        """
        Returns: all HasPermissions which the user has direct and
                    indirect (through membership in a group or rlc) as list
        """
        if self.is_superuser:
            return HasPermission.objects.all()
        return self.__get_as_user_permissions() + self.__get_as_group_member_permissions() + \
               self.__get_as_rlc_member_permissions()

    def __get_as_user_special_permissions(self, permission_id):
        """
        Args:
            permission_id: (int) permissionId with the queryset is filtered

        Returns: all HasPermissions the user itself has with permission_id as permission as list
        """
        return list(HasPermission.objects.filter(user_has_permission=self.pk, permission_id=permission_id))

    def __get_as_group_member_special_permissions(self, permission):
        groups = [groups['id'] for groups in list(self.group_members.values('id'))]
        return list(HasPermission.objects.filter(group_has_permission_id__in=groups, permission_id=permission))

    def __get_as_rlc_member_special_permissions(self, permission):
        return list(HasPermission.objects.filter(rlc_has_permission_id=self.rlc.id, permission_id=permission))

    def get_overall_special_permissions(self, permission):
        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission).id
        return self.__get_as_user_special_permissions(permission) + self.__get_as_group_member_special_permissions(
            permission) + self.__get_as_rlc_member_special_permissions(permission)

    def __has_as_user_permission(self, permission, for_user=None, for_group=None, for_rlc=None):
        return HasPermission.objects.filter(user_has_permission=self.pk, permission_id=permission,
                                            permission_for_user_id=for_user,
                                            permission_for_group_id=for_group,
                                            permission_for_rlc_id=for_rlc).count() >= 1

    def __has_as_group_member_permission(self, permission, for_user=None, for_group=None, for_rlc=None):
        groups = [groups['id'] for groups in list(self.group_members.values('id'))]
        return HasPermission.objects.filter(group_has_permission_id__in=groups, permission_id=permission,
                                            permission_for_user_id=for_user,
                                            permission_for_group_id=for_group,
                                            permission_for_rlc_id=for_rlc).count() >= 1

    def __has_as_rlc_member_permission(self, permission, for_user=None, for_group=None, for_rlc=None):
        if not self.rlc:
            return False

        return HasPermission.objects.filter(rlc_has_permission_id=self.rlc.id, permission_id=permission,
                                            permission_for_user_id=for_user,
                                            permission_for_group_id=for_group,
                                            permission_for_rlc_id=for_rlc).count() >= 1

    def has_permission(self, permission, for_user=None, for_group=None, for_rlc=None):
        """
        Args:
            permission: (int) permission_id or (str) exact name of permission
            for_user: (int) user_id for which the permission is
            for_group: (int) group_id for which the permission is
            for_rlc: (int) rlc_id for which the permission is

        Returns:
            True if the user has the given permission for the given group or user
            False if the user doesnt have the permission
        """
        if isinstance(permission, str):
            try:
                permission = Permission.objects.get(name=permission).id
            except Exception as e:
                raise CustomError(ERROR__API__PERMISSION__NOT_FOUND)
        if for_user is not None and for_group is not None and for_rlc is not None:
            raise AttributeError()

        return self.__has_as_user_permission(permission, for_user, for_group, for_rlc) or \
               self.__has_as_group_member_permission(permission, for_user, for_group, for_rlc) or \
               self.__has_as_rlc_member_permission(permission, for_user, for_group, for_rlc) or \
               self.is_superuser
