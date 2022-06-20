from django.db import models

from .user import UserProfile


class StatisticUser(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="statistic_user"
    )
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "StatisticUser"
        verbose_name_plural = "StatisticUsers"
        ordering = ["user__name"]

    def __str__(self):
        return "statisticUser: {}; email: {};".format(self.pk, self.user.email)

    def change_password(self, old_password, new_password):
        if not self.user.check_password(old_password):
            raise ValueError("The password is not correct.")
        if hasattr(self.user, "rlc_user"):
            raise ValueError(
                "You also have an lc role, please change your password within Law&Orga."
            )
        self.user.set_password(new_password)
        self.user.save()
