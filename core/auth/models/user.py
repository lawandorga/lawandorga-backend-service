from typing import TYPE_CHECKING, Union

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from rest_framework.exceptions import ParseError

if TYPE_CHECKING:
    from core.models import MailUser, MatrixUser, Permission, RlcUser, StatisticUser


class UserProfileManager(BaseUserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("rlc_user", "statistic_user", "internal_user", "mail_user")
        )


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # custom manager
    objects = UserProfileManager()

    # overwrites abstract base user
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    # mypy stuff
    rlc_user: "RlcUser"
    statistic_user: "StatisticUser"
    matrix_user: "MatrixUser"
    mail_user: "MailUser"

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"
        ordering = ["name"]

    def __str__(self):
        return "user: {}; email: {};".format(self.pk, self.email)

    @property
    def is_staff(self):
        # django intern stuff
        return hasattr(self, "internal_user")

    @property
    def rlc(self):
        return self.rlc_user.org

    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            raise ParseError("The password is not correct.")
        rlc_user = self.rlc_user
        self.set_password(new_password)
        rlc_user.change_password_for_keys(new_password)
        with transaction.atomic():
            rlc_user.save()
            self.save()

    def has_permission(self, permission: Union[str, "Permission"]) -> bool:
        return self.rlc_user.has_permission(permission)

    def get_collab_permissions(self):
        from core.models import PermissionForCollabDocument

        groups = self.rlc_user.groups.all()
        return PermissionForCollabDocument.objects.filter(
            group_has_permission__in=groups
        ).select_related("document")

    def get_public_key(self) -> bytes:
        return self.rlc_user.get_public_key()

    def get_private_key(self, *args, **kwargs) -> str:
        return self.rlc_user.get_private_key()

    def get_private_key_rlc(self, private_key_user=None, request=None):
        if private_key_user:
            pass
        elif request:
            private_key_user = self.get_private_key(request=request)
        else:
            raise ValueError("You need to pass (private_key_user) or (request).")

        return self.rlc.get_private_key(user=self, private_key_user=private_key_user)

    def get_rlc_aes_key(self, private_key_user=None):
        if private_key_user:
            return self.rlc.get_aes_key(user=self, private_key_user=private_key_user)
        else:
            raise ValueError("You need to set (private_key_user).")

    def test_all_keys(self, private_key_user):
        self.users_rlc_keys.first().test(private_key_user)

    def generate_keys_for_user(self, private_key_self, user_to_unlock):
        """
        this method assumes that a valid public key exists for user_to_unlock
        """
        from core.models import OrgEncryption
        from core.records.models import RecordEncryptionNew

        # check if all keys can be handed over
        success = True

        # generate new rlc key - this always works
        user_to_unlock.users_rlc_keys.all().delete()
        aes_key_rlc = self.rlc.get_aes_key(user=self, private_key_user=private_key_self)
        new_keys = OrgEncryption(
            user=user_to_unlock, rlc=user_to_unlock.rlc, encrypted_key=aes_key_rlc
        )
        new_keys.encrypt(user_to_unlock.get_public_key())
        new_keys.save()

        # generate new record encryption
        record_encryptions = user_to_unlock.rlc_user.recordencryptions.filter(
            correct=False
        )

        for old_keys in list(record_encryptions):
            # change the keys to the new keys
            try:
                encryption = RecordEncryptionNew.objects.get(
                    user=self.rlc_user, record=old_keys.record
                )
            except ObjectDoesNotExist:
                success = False
                continue
            encryption.decrypt(private_key_user=private_key_self)
            old_keys.key = encryption.key
            old_keys.encrypt(user_to_unlock.get_public_key())
            old_keys.save()

        # return true if everything worked as expected return false otherwise
        return success
