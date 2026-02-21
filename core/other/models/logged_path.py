from django.db import models
from django.utils import timezone

from core.models import UserProfile


class LoggedPath(models.Model):
    path = models.CharField(max_length=200, db_index=True)
    user = models.ForeignKey(
        UserProfile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="logged_paths",
    )
    time = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.IntegerField(default=0)
    method = models.CharField(default="UNKNOWN", max_length=20)

    class Meta:
        ordering = ["-time"]
        verbose_name = "OTH_LoggedPath"
        verbose_name_plural = "OTH_LoggedPaths"

    def __str__(self):
        return "loggedPath: {}; path: {} '{}' {}; user: {};".format(
            timezone.localtime(self.time).strftime("%Y-%m-%d %H:%M"),
            self.method,
            self.path,
            self.status,
            self.get_email(),
        )

    def get_email(self):
        if self.user:
            return self.user.email
        return None
