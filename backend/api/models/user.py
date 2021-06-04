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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.request import Request
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from backend.api.errors import CustomError
from backend.api.models.has_permission import HasPermission
from backend.api.models.permission import Permission
from backend.static.encryption import RSAEncryption
from backend.static.error_codes import (
    ERROR__API__RLC__NO_PUBLIC_KEY_FOUND,
    ERROR__API__USER__NO_PRIVATE_KEY_PROVIDED,
)
from backend.static.permissions import PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC


class UserProfileManager(BaseUserManager):
    @staticmethod
    def get_users_with_special_permission(permission, from_rlc=None, for_rlc=None):
        if isinstance(permission, str):
            permission = Permission.objects.get(name=permission).id

        users = (
            HasPermission.objects.filter(
                permission=permission,
                group_has_permission=None,
                rlc_has_permission=None
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
            rlc_has_permission=None
        ).values("group_has_permission")
        group_ids = [
            has_permission["group_has_permission"] for has_permission in groups
        ]
        result = (
            result | UserProfile.objects.filter(rlcgroups__in=group_ids).distinct()
        )
        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        rlcs = HasPermission.objects.filter(
            permission=permission,
            user_has_permission=None,
            group_has_permission=None
        ).values("rlc_has_permission")
        rlc_ids = [has_permission["rlc_has_permission"] for has_permission in rlcs]
        result = result | UserProfile.objects.filter(rlc__in=rlc_ids).distinct()

        if from_rlc is not None:
            result = result.filter(rlc=from_rlc)

        return result


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    email_confirmed = models.BooleanField(default=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=17, null=True, default=None, blank=True)
    street = models.CharField(max_length=255, default=None, null=True, blank=True)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)
    postal_code = models.CharField(max_length=255, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    rlc = models.ForeignKey("Rlc", related_name="rlc_members", on_delete=models.PROTECT, blank=True, null=True)

    # custom manager
    objects = UserProfileManager()

    # overwrites abstract base user
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
        ordering = ["name"]

    def __str__(self):
        return "user: {}; email: {};".format(self.pk, self.email)

    # django intern stuff
    @property
    def is_staff(self):
        return hasattr(self, 'internal_user')

    # other stuff
    def __get_as_user_permissions(self):
        """
        Returns: all HasPermissions the user itself has as list
        """
        return list(HasPermission.objects.filter(user_has_permission=self.pk))

    def __get_as_group_member_permissions(self):
        """
        Returns: all HasPermissions the groups in which the user is member of have as list
        """
        groups = [groups["id"] for groups in list(self.rlcgroups.values("id"))]
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

    def __has_as_user_permission(self, permission):
        return HasPermission.objects.filter(user_has_permission=self.pk, permission=permission).exists()

    def __has_as_group_member_permission(self, permission):
        groups = [group.pk for group in self.rlcgroups.all()]
        return HasPermission.objects.filter(group_has_permission__pk__in=groups, permission=permission).exists()

    def __has_as_rlc_member_permission(self, permission):
        return HasPermission.objects.filter(rlc_has_permission=self.rlc, permission=permission).exists()

    def has_permission(self, permission, for_user=None, for_group=None, for_rlc=None):
        if isinstance(permission, str):
            permission, created = Permission.objects.get_or_create(name=permission)

        as_user = self.__has_as_user_permission(permission)
        as_group = self.__has_as_group_member_permission(permission)
        as_rlc = self.__has_as_rlc_member_permission(permission)

        return as_user or as_group or as_rlc

    def has_permissions(self, permissions):
        return any(map(lambda permission: self.has_permission(permission), permissions))

    def get_permissions(self):
        user_permissions = HasPermission.objects.filter(user_has_permission=self)
        user_groups = self.rlcgroups.all()
        group_permissions = HasPermission.objects.filter(group_has_permission__in=user_groups)
        rlc_permissions = HasPermission.objects.filter(rlc_has_permission=self.rlc)
        return user_permissions | group_permissions | rlc_permissions

    def get_public_key(self) -> str:
        """
        gets the public key of the user from the database
        :return: public key of user (PEM)
        """
        if not hasattr(self, "encryption_keys"):
            self.generate_new_user_encryption_keys()
        return self.encryption_keys.public_key

    def get_private_key(self, password_user: str = None, request: Request = None) -> str:
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
                    return self.encryption_keys.decrypt_private_key(settings.DUMMY_USER_PASSWORD)
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
        # assert self.has_permission(PERMISSION_VIEW_RECORDS_FULL_DETAIL_RLC)

        # this variable checks if all keys that the user needed were generated
        keys_missing = False

        # generate new rlc key - this works always
        user_to_unlock.users_rlc_keys.all().delete()
        aes_key_rlc = self.rlc.get_aes_key(user=self, private_key_user=private_key_self)
        new_keys = UsersRlcKeys(
            user=user_to_unlock, rlc=user_to_unlock.rlc, encrypted_key=aes_key_rlc
        )
        new_keys.encrypt(user_to_unlock.get_public_key())
        new_keys.save()

        # generate new record encryption
        record_encryptions = user_to_unlock.record_encryptions.all()

        for old_keys in list(record_encryptions):
            # check if the user has the needed keys if not just skip
            try:
                encryption = RecordEncryption.objects.get(user=self, record=old_keys.record)
            except ObjectDoesNotExist:
                keys_missing = True
                continue
            # change the keys to the new keys
            encryption.decrypt(private_key_user=private_key_self)
            old_keys.encrypted_key = encryption.encrypted_key
            old_keys.encrypt(user_to_unlock.get_public_key())
            old_keys.save()

        # return true if everything worked as expected return false otherwise
        return not keys_missing


class RlcUser(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='rlc_user')
    email_confirmed = models.BooleanField(default=True)
    birthday = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=17, null=True, default=None, blank=True)
    street = models.CharField(max_length=255, default=None, null=True, blank=True)
    city = models.CharField(max_length=255, default=None, null=True, blank=True)
    postal_code = models.CharField(max_length=255, default=None, null=True, blank=True)
    locked = models.BooleanField(default=False)
    rlc = models.ForeignKey("Rlc", related_name="users", on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name = 'RlcUser'
        verbose_name_plural = 'RlcUsers'

    def __str__(self):
        return 'rlcUser: {};'.format(self.user.email)


# create a rlc user when a normal user is saved
@receiver(post_save, sender=UserProfile)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    rlc_user, created = RlcUser.objects.get_or_create(user=instance)
    if instance.rlc:
        rlc_user.phone_number = instance.phone_number
        rlc_user.birthday = instance.birthday
        rlc_user.street = instance.street
        rlc_user.city = instance.city
        rlc_user.postal_code = instance.postal_code
        rlc_user.email_confirmed = instance.email_confirmed
        rlc_user.rlc = instance.rlc
        rlc_user.locked = instance.locked
    rlc_user.save()


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
