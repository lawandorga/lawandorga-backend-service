from django.db import models

from .user import UserProfile


class InternalUser(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="internal_user"
    )

    class Meta:
        verbose_name = "InternalUser"
        verbose_name_plural = "InternalUsers"

    def __str__(self):
        return "internalUser: {};".format(self.user.email)

    def check_login_allowed(self):
        # login is always allowed
        pass
