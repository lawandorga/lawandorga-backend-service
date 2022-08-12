
from django.db import models
from django.utils import timezone

from .notification_group import NotificationGroup
from .. import UserProfile
from apps.static.notification_enums import NotificationType


class Notification(models.Model):
    notification_group = models.ForeignKey(
        NotificationGroup,
        related_name="notifications",
        on_delete=models.CASCADE,
        null=True,
    )
    source_user = models.ForeignKey(
        UserProfile,
        related_name="notification_caused",
        on_delete=models.SET_NULL,
        null=True,
    )
    created = models.DateTimeField(default=timezone.now)
    type = models.CharField(
        max_length=75, choices=NotificationType.choices(), null=False, default=""
    )
    read = models.BooleanField(default=False, null=False)
    text = models.TextField(null=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return "notification: {};".format(self.id)

    def save(self, *args, **kwargs):
        if not self.read and self.id is None:
            self.notification_group.new_activity()
        super().save()
        all_in_group_read = self.notification_group.all_notifications_read()
        if all_in_group_read and not self.notification_group.read:
            self.notification_group.read = True
            self.notification_group.save()
        elif not all_in_group_read and self.notification_group.read:
            self.notification_group.read = False
            self.notification_group.save()
