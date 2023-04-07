from uuid import UUID, uuid4

from folders.domain.value_objects.box import OpenBox

from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.folders.domain.types import StrDict
from core.timeline.utils import camel_to_snake_case
from messagebus import Event


class EventSourced:
    def __init__(self, events: list[Event]) -> None:
        for event in events:
            self.mutate(event)
        self.new_events: list[Event] = []

    def mutate(self, event: Event):
        action = camel_to_snake_case(event.action)
        func = getattr(self, f"when_{action}")
        func(event)

    # def generate_event(self, event: Event) -> Event:
    #     pass

    def apply(self, event: Event):
        self.new_events.append(event)
        self.mutate(event)


class TimelineEvent(EventSourced):
    class Created(Event):
        text_box: StrDict
        uuid: UUID = uuid4()

    @classmethod
    def create(cls, text: str, folder: Folder, by: RlcUser):
        event = TimelineEvent()
        open_box = OpenBox.create_from_string(text)
        key = folder.get_encryption_key(requestor=by)
        locked_box = key.lock(open_box)
        event.apply(TimelineEvent.Created(text_box=locked_box.as_dict()))
        return event

    def __init__(self, events: list[Event] = []):
        super().__init__(events)

    def when_created(self, event: Created):
        # self.text = event.text
        self.uuid = event.uuid

    def when_information_updated(self, text=None):
        if text is not None:
            self.text = text

    def when_deleted(self):
        pass
