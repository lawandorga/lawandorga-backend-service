from django.db import models
from django.utils import timezone

from messagebus.domain.message import DomainMessage


class Message(models.Model):
    stream_name = models.CharField(max_length=1000)
    action = models.SlugField(max_length=200)
    position = models.IntegerField()
    data = models.JSONField()
    metadata = models.JSONField()
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        unique_together = ["position", "stream_name"]

    def __str__(self):
        return f"{self.stream_name}: {self.data}"

    def to_domain_message(self):
        return DomainMessage(
            stream_name=self.stream_name,
            action=self.action,
            data=self.data,
            metadata=self.metadata,
            position=self.position,
            time=self.time,
        )
