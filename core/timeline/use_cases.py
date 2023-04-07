

from core.auth.models.org_user import RlcUser
from core.seedwork.use_case_layer import use_case
from core.timeline.domain import TimelineEvent
from core.timeline.repository import TimelineEventRepository


@use_case
def create_timeline_event(__actor: RlcUser, text: str):
    event = TimelineEvent.create(text=text)
    TimelineEventRepository.save(event)
    return event
