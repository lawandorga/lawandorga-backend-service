from django.conf import settings

from messagebus.domain.store import EventStore
from messagebus.impl.store import DjangoEventStore, InMemoryEventStore


def test_settings_repository():
    r = EventStore()
    assert isinstance(r, DjangoEventStore)
    settings.MESSAGEBUS_EVENT_STORE = (
        "messagebus.impl.store.InMemoryEventStore"
    )
    r = EventStore()
    assert isinstance(r, InMemoryEventStore)
