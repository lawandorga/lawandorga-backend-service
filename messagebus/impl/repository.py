from typing import Any, Optional
from uuid import UUID

from django.db import models
from django.db.models import Max
from django.utils import timezone

from messagebus.domain.event import Event
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

    def __str__(self):
        return f"{self.stream_name}: {self.data}"

    @property
    def _name(self):
        return f"{self.stream_name.split('-')[0]}.{self.action}"

    @property
    def _aggregate_uuid(self):
        return UUID("".join(self.stream_name.split("-")[1:]))


class InMemoryMessageBusRepository(MessageBusRepository):
    messages: list[Message] = []

    @classmethod
    def save_event(cls, event: Event, position: Optional[int] = None) -> Event:
        if not hasattr(cls, "messages"):
            cls.messages = []

        if position is None:
            position = 1
            for m in cls.messages:
                if m.stream_name == event.stream_name:
                    position += 1

        message: Message = Message(
            stream_name=event.stream_name,
            action=event.action,
            position=position,
            data=event.data,
            metadata=event.metadata,
        )
        cls.messages.append(message)
        event = create_event_from_message(message)
        return event

    @classmethod
    def save_command(cls, command: Any, position: Optional[int]) -> Any:
        raise NotImplementedError()


class DjangoMessageBusRepository(MessageBusRepository):
    @classmethod
    def save_event(cls, raw_event: Event, position: Optional[int] = None) -> Event:
        if position is None:
            messages_max = Message.objects.filter(
                stream_name=raw_event.stream_name
            ).aggregate(max_position=Max("position"))
            position = (
                messages_max["max_position"] + 1 if messages_max["max_position"] else 1
            )

        message = Message(
            stream_name=raw_event.stream_name,
            action=raw_event.action,
            position=position,
            data=raw_event.data,
            metadata=raw_event.metadata,
        )
        message.save()
        return create_event_from_message(message)

    @classmethod
    def save_command(cls, command: Any, position: Optional[int]) -> Any:
        raise NotImplementedError()
