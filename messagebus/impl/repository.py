from typing import Any, Optional

from django.db import models
from django.db.models import Max
from django.utils import timezone

from messagebus.domain.event import Event, RawEvent
from messagebus.domain.repository import MessageBusRepository
from messagebus.impl.factory import create_event_from_message


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


class DjangoMessageBusRepository(MessageBusRepository):
    @classmethod
    def save_event(cls, event: RawEvent, position: Optional[int] = None) -> Event:
        if position is None:
            messages_max = Message.objects.filter(
                stream_name=event.stream_name
            ).aggregate(max_position=Max("position"))
            position = (
                messages_max["max_position"] + 1 if messages_max["max_position"] else 1
            )

        message = Message(
            stream_name=event.stream_name,
            action=event.name,
            position=position,
            data=event.data.to_dict(),
            metadata=event.metadata,
        )
        message.save()
        return create_event_from_message(message)

    @classmethod
    def save_command(cls, command: Any, position: Optional[int]) -> Any:
        raise NotImplementedError()
