from core.auth.models.org_user import RlcUser
from core.folders.domain.aggregates.folder import Folder
from core.seedwork.use_case_layer import use_case
from core.timeline.domain import TimelineEvent
from core.timeline.repository import TimelineEventRepository


@use_case
def create_timeline_event(__actor: RlcUser, text: str, folder: Folder):
    event = TimelineEvent.create(text=text, by=__actor, folder=folder)
    TimelineEventRepository.save(event)
    return event
