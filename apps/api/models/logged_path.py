from django.db import models
from django.utils import timezone

from apps.api.models import UserProfile


class LoggedPath(models.Model):
    path = models.CharField(max_length=200)
    user = models.ForeignKey(
        UserProfile,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="logged_paths",
    )
    time = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    method = models.CharField(default="UNKNOWN", max_length=20)
    data = models.TextField(blank=True)

    class Meta:
        ordering = ["-time"]
        verbose_name = "LoggedPath"
        verbose_name_plural = "LoggedPaths"

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
