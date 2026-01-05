from typing import TYPE_CHECKING, Optional, Union

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from core.seedwork.domain_layer import DomainError

if TYPE_CHECKING:
    from core.models import MailUser, MatrixUser, OrgUser, Permission, StatisticUser
    from core.org.models.org_encryption import OrgEncryption


class UserProfileManager(BaseUserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("org_user", "statistic_user", "internal_user", "mail_user")
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

    if TYPE_CHECKING:
        users_rlc_keys: models.QuerySet["OrgEncryption"]
        org_user: "OrgUser"
        statistic_user: "StatisticUser"
        matrix_user: "MatrixUser"
        mail_user: "MailUser"

    class Meta:
        verbose_name = "AUT_User"
        verbose_name_plural = "AUT_Users"
        ordering = ["name"]

    def __str__(self):
        return "user: {}; email: {};".format(self.pk, self.email)

    @property
    def is_staff(self):
        # django intern stuff
        return hasattr(self, "internal_user")

    @property
    def last_login_month(self) -> Optional[str]:
        if self.last_login is None:
            return None
        return self.last_login.strftime("%b %Y")

    @property
    def org(self):
        return self.org_user.org

    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            raise DomainError("The password is not correct.")
        self.set_password(new_password)
        if hasattr(self, "org_user"):
            org_user = self.org_user
            new_key = org_user.keyring.change_password(new_password)
            org_user.change_password_for_keys(new_key)
            return [self, org_user, org_user.keyring]
        return [self]

    def has_permission(self, permission: Union[str, "Permission"]) -> bool:
        return self.org_user.has_permission(permission)

    def get_public_key(self) -> bytes:
        return self.org_user.get_public_key()

    def get_private_key(self, *args, **kwargs) -> str:
        return self.org_user.get_private_key()

    def get_org_aes_key(self, private_key_user=None):
        if private_key_user:
            return self.org.get_aes_key(user=self, private_key_user=private_key_user)
        else:
            raise ValueError("You need to set (private_key_user).")

    def test_all_keys(self, private_key_user):
        self.users_rlc_keys.get().test(private_key_user)
