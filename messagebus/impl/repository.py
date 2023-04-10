from typing import Optional

from django.db import models
from django.db.models import Max
from django.utils import timezone

from messagebus.domain.message import DomainMessage
from messagebus.domain.repository import M, MessageBusRepository


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


class InMemoryMessageBusRepository(MessageBusRepository):
    messages: list[Message] = []

    @classmethod
    def save_message(cls, m: M, position: Optional[int] = None) -> M:
        if not hasattr(cls, "messages"):
            cls.messages = []

        if position is None:
            position = 1
            for saved_message in cls.messages:
                if saved_message.stream_name == m.stream_name:
                    position += 1

        message: Message = Message(
            stream_name=m.stream_name,
            action=m.action,
            position=position,
            data=m.data,
            metadata=m.metadata,
        )
        cls.messages.append(message)

        m.set_position(message.position)
        m.set_time(message.time)

        return m


class DjangoMessageBusRepository(MessageBusRepository):
    @classmethod
    def save_message(cls, m: M, position: Optional[int] = None) -> M:
        if position is None:
            messages_max = Message.objects.filter(stream_name=m.stream_name).aggregate(
                max_position=Max("position")
            )
            position = (
                messages_max["max_position"] + 1 if messages_max["max_position"] else 1
            )

        message = Message(
            stream_name=m.stream_name,
            action=m.action,
            position=position,
            data=m.data,
            metadata=m.metadata,
        )
        message.save()

        m.set_position(message.position)
        m.set_time(message.time)

        return m
