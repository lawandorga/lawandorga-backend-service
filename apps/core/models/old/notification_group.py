from django.db import models
from django.utils import timezone

from apps.static.notification_enums import NotificationGroupType

from .. import UserProfile


class NotificationGroup(models.Model):
    user = models.ForeignKey(
        UserProfile, related_name="notification_groups", on_delete=models.CASCADE
    )
    last_activity = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now)

    type = models.CharField(
        max_length=100, choices=NotificationGroupType.choices(), null=False
    )
    read = models.BooleanField(default=False, null=False)

    ref_id = models.CharField(max_length=50, null=False)
    ref_text = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name = "NotificationGroup"
        verbose_name_plural = "NotificationGroups"

    def __str__(self):
        return "notificationGroup: {}; user: {};".format(self.pk, self.user.email)

    def new_activity(self):
        self.last_activity = timezone.now()
        self.read = False
        self.save()

    def all_notifications_read(self) -> bool:
        return (
            self.notifications.count() > 0
            and self.notifications.filter(read=False).count() == 0
        )
