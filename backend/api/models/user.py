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
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
from rest_framework.request import Request
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from backend.api.errors import CustomError
from backend.api.models.has_permission import HasPermission
from backend.api.models.permission import Permission
from backend.static.encryption import RSAEncryption
from backend.static.error_codes import (
    ERROR__API__PERMISSION__NOT_FOUND,
    ERROR__API__RLC__NO_PUBLIC_KEY_FOUND,
    ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED,
)
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC


class UserProfileManager(BaseUserManager):
    @staticmethod
    def get_users_with_special_permission(
        permission, from_rlc=None, for_user=None, for_group=None, for_rlc=None,
    ):
        """
        returns all users
        :param permission:
        :param from_rlc:
        :param for_user:
        :param for_group:
        :param for_rlc:
        :return:
        """

        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission).id
        if for_user is not None and for_group is not None and for_rlc is not None:
            raise AttributeError()
        users = (
            HasPermission.objects.filter(
                permission=permission,
                group_has_permission=None,
                rlc_has_permission=None,
                permission_for_user=for_user,
                permission_for_group=for_group,
                permission_for_rlc=for_rlc,
            )
            .values("user_has_permission")
            .distinct()
        )

        user_ids = [has_permission["user_has_permission"] for has_permission in users]
        result = UserProfile.objects.filter(id__in=user_ids).distinct()
        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        groups = HasPermission.objects.filter(
            permission=permission,
            user_has_permission=None,
            rlc_has_permission=None,
            permission_for_user=for_user,
            permission_for_group=for_group,
            permission_for_rlc=for_rlc,
        ).values("group_has_permission")
        group_ids = [
            has_permission["group_has_permission"] for has_permission in groups
        ]
        result = (
            result | UserProfile.objects.filter(group_members__in=group_ids).distinct()
        )

        rlcs = HasPermission.objects.filter(
            permission=permission,
            user_has_permission=None,
            group_has_permission=None,
            permission_for_user=for_user,
            permission_for_group=for_group,
            permission_for_rlc=for_rlc,
        ).values("rlc_has_permission")
        rlc_ids = [has_permission["rlc_has_permission"] for has_permission in rlcs]
        result = result | UserProfile.objects.filter(rlc__in=rlc_ids).distinct()

        return result

    @staticmethod
    def get_users_with_special_permissions(
        permissions, from_rlc=None, for_user=None, for_group=None, for_rlc=None,
    ):
        users = None
        for permission in permissions:
            users_to_add = UserProfileManager.get_users_with_special_permission(
                permission, from_rlc, for_user, for_group, for_rlc
            )
            if users is None:
                users = users_to_add
            else:
                users = users.union(users_to_add).distinct()
        return users


class UserProfile(
    ExportModelOperationsMixin("user"), AbstractBaseUser, PermissionsMixin
):
    """ profile of users """

    email = models.EmailField(max_length=255, unique=True)
    email_confirmed = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=17, null=True, default=None, blank=True)

    # address
    street = models.CharField(max_length=255, default=None, null=True, blank=True)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)
    postal_code = models.CharField(max_length=255, default=None, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    locked = models.BooleanField(default=False)

    rlc = models.ForeignKey("Rlc", related_name="rlc_members", on_delete=models.PROTECT)
    objects = UserProfileManager()

    user_states_possible = (
        ("ac", "active"),
        ("ia", "inactive"),
        ("ex", "exam"),
        ("ab", "abroad"),
    )
    user_state = models.CharField(max_length=2, choices=user_states_possible)

    user_record_states_possible = (
        ("ac", "accepting"),
        ("na", "not accepting"),
        ("de", "depends"),
    )
    user_record_state = models.CharField(
        max_length=2, choices=user_record_states_possible
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]  # email already in there, other are default

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def __str__(self):
        return "user: {}; email: {};".format(self.pk, self.email)

    def __get_as_user_permissions(self):
        """
        Returns: all HasPermissions the user itself has as list
        """
        return list(HasPermission.objects.filter(user_has_permission=self.pk))

    def __get_as_group_member_permissions(self):
        """
        Returns: all HasPermissions the groups in which the user is member of have as list
        """
        groups = [groups["id"] for groups in list(self.group_members.values("id"))]
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
        return (
            self.__get_as_user_permissions()
            + self.__get_as_group_member_permissions()
            + self.__get_as_rlc_member_permissions()
        )

    def __get_as_user_special_permissions(self, permission_id):
        """
        Args:
            permission_id: (int) permissionId with the queryset is filtered

        Returns: all HasPermissions the user itself has with permission_id as permission as list
        """
        return list(
            HasPermission.objects.filter(
                user_has_permission=self.pk, permission_id=permission_id
            )
        )

    def __get_as_group_member_special_permissions(self, permission):
        groups = [groups["id"] for groups in list(self.group_members.values("id"))]
        return list(
            HasPermission.objects.filter(
                group_has_permission_id__in=groups, permission_id=permission
            )
        )

    def __get_as_rlc_member_special_permissions(self, permission):
        return list(
            HasPermission.objects.filter(
                rlc_has_permission_id=self.rlc.id, permission_id=permission
            )
        )

    def get_overall_special_permissions(self, permission):
        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission).id
        return (
            self.__get_as_user_special_permissions(permission)
            + self.__get_as_group_member_special_permissions(permission)
            + self.__get_as_rlc_member_special_permissions(permission)
        )

    def __has_as_user_permission(
        self, permission, for_user=None, for_group=None, for_rlc=None
    ):
        return (
            HasPermission.objects.filter(
                user_has_permission=self.pk, permission_id=permission,
            ).count()
            >= 1
        )

    def __has_as_group_member_permission(
        self, permission, for_user=None, for_group=None, for_rlc=None
    ):
        groups = [groups["id"] for groups in list(self.group_members.values("id"))]
        return (
            HasPermission.objects.filter(
                group_has_permission_id__in=groups, permission_id=permission,
            ).count()
            >= 1
        )

    def __has_as_rlc_member_permission(
        self, permission, for_user=None, for_group=None, for_rlc=None
    ):
        if not self.rlc:
            return False

        return (
            HasPermission.objects.filter(
                rlc_has_permission_id=self.rlc.id, permission_id=permission,
            ).count()
            >= 1
        )

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

        return (
            self.__has_as_user_permission(permission, for_user, for_group, for_rlc)
            or self.__has_as_group_member_permission(
                permission, for_user, for_group, for_rlc
            )
            or self.__has_as_rlc_member_permission(
                permission, for_user, for_group, for_rlc
            )
            or self.is_superuser
        )

    def get_public_key(self) -> str:
        """
        gets the public key of the user from the database
        :return: public key of user (PEM)
        """
        if not hasattr(self, "encryption_keys"):
            self.generate_new_user_encryption_keys()
        return self.encryption_keys.public_key

    def get_private_key(
        self, password_user: str = None, request: Request = None
    ) -> str:
        if not hasattr(self, "encryption_keys"):
            self.generate_new_user_encryption_keys()

        if password_user and not request:
            private_key = self.encryption_keys.decrypt_private_key(password_user)

        elif request and not password_user:
            private_key = request.META.get("HTTP_PRIVATE_KEY")
            if not private_key:
                # enable direct testing of the rest framework
                if (
                    settings.DEBUG
                    and self.email == "dummy@rlcm.de"
                    and settings.DUMMY_USER_PASSWORD
                ):
                    return self.encryption_keys.decrypt_private_key(
                        settings.DUMMY_USER_PASSWORD
                    )
                else:
                    raise CustomError(ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED)
            private_key = private_key.replace("\\n", "\n").replace("<linebreak>", "\n")

        else:
            raise ValueError("You need to pass (password_user) or (request).")

        return private_key

    def get_rlcs_public_key(self):
        return self.rlc.get_public_key()

    def get_rlcs_private_key(self, users_private_key):
        from backend.api.models.rlc_encryption_keys import RlcEncryptionKeys

        try:
            rlc_keys = RlcEncryptionKeys.objects.get(rlc=self.rlc)
        except:
            raise CustomError(ERROR__API__RLC__NO_PUBLIC_KEY_FOUND)
        aes_rlc_key = self.get_rlcs_aes_key(users_private_key)
        rlcs_private_key = rlc_keys.decrypt_private_key(aes_rlc_key)
        return rlcs_private_key

    def get_rlcs_aes_key(self, users_private_key):
        from backend.api.models.users_rlc_keys import UsersRlcKeys

        # check if there is only one usersRlcKey
        keys = UsersRlcKeys.objects.filter(user=self)
        users_rlc_keys = keys.first()
        rlc_encrypted_key_for_user = users_rlc_keys.encrypted_key
        try:
            rlc_encrypted_key_for_user = rlc_encrypted_key_for_user.tobytes()
        except:
            pass
        return RSAEncryption.decrypt(rlc_encrypted_key_for_user, users_private_key)

    def generate_new_user_encryption_keys(self):

        from backend.api.models.user_encryption_keys import UserEncryptionKeys

        UserEncryptionKeys.objects.filter(user=self).delete()
        private, public = RSAEncryption.generate_keys()
        user_keys = UserEncryptionKeys(
            user=self, private_key=private, public_key=public
        )
        user_keys.save()

    def generate_rlc_keys_for_this_user(self, rlcs_aes_key):

        # delete (maybe) old existing rlc keys
        from backend.api.models.users_rlc_keys import UsersRlcKeys

        UsersRlcKeys.objects.filter(user=self, rlc=self.rlc).delete()

        own_public_key = self.get_public_key()
        encrypted_key = RSAEncryption.encrypt(rlcs_aes_key, own_public_key)
        users_rlc_keys = UsersRlcKeys(
            user=self, rlc=self.rlc, encrypted_key=encrypted_key
        )
        users_rlc_keys.save()

    def rsa_encrypt(self, plain):
        from backend.static.encryption import RSAEncryption

        return RSAEncryption.encrypt(plain, self.get_public_key())

    def generate_keys_for_user(self, private_key_self, user_to_unlock):
        """
        this method assumes that a valid public key exists for user_to_unlock
        """
        from backend.api.models import UsersRlcKeys
        from backend.recordmanagement.models import RecordEncryption

        # assert that the self user has all possible keys
        assert self.has_permission(PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC)

        # generate new rlc key
        user_to_unlock.users_rlc_keys.all().delete()
        aes_key_rlc = self.rlc.get_aes_key(user=self, private_key_user=private_key_self)
        new_keys = UsersRlcKeys(
            user=user_to_unlock, rlc=user_to_unlock.rlc, encrypted_key=aes_key_rlc
        )
        new_keys.encrypt(user_to_unlock.get_public_key())
        new_keys.save()

        # generate new record encryption
        record_encryptions = user_to_unlock.record_encryptions.all()
        record_encryptions_list = list(record_encryptions)
        record_encryptions.delete()

        for old_keys in record_encryptions_list:
            encryption = RecordEncryption.objects.get(user=self, record=old_keys.record)
            encryption.decrypt(private_key_user=private_key_self)
            new_keys = RecordEncryption(
                user=user_to_unlock,
                record=old_keys.record,
                encrypted_key=encryption.encrypted_key,
            )
            new_keys.encrypt(user_to_unlock.get_public_key())
            new_keys.save()


# this is used on signup
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        login_timestamp = (
            ""
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None)
        )
        super_make_hash_value = (
            str(user.pk) + user.password + str(login_timestamp) + str(timestamp)
        )
        additional_hash_value = str(user.email_confirmed)
        return super_make_hash_value + additional_hash_value


account_activation_token = AccountActivationTokenGenerator()

# this is used on password reset
password_reset_token = PasswordResetTokenGenerator()
