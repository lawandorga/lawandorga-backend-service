from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.seedwork.use_case_layer import use_case
from core.timeline.domain import TimelineEvent
from core.timeline.repository import TimelineEventRepository
from messagebus.domain.store import EventStore


@use_case
def create_timeline_event(__actor: RlcUser, text: str, folder_uuid: UUID):
    event = TimelineEvent.create(
        text=text, folder_uuid=folder_uuid, org_pk=__actor.org_id, by=__actor.uuid
    )
    TimelineEventRepository(EventStore()).save(event, by=__actor)
    return event
