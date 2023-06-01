from datetime import datetime
from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import use_case
from core.timeline.domain import TimelineEvent
from core.timeline.repository import TimelineEventRepository
from messagebus.domain.store import EventStore


@use_case
def create_timeline_event(
    __actor: RlcUser, text: str, time: datetime, folder_uuid: UUID
):
    event = TimelineEvent.create(
        text=text,
        folder_uuid=folder_uuid,
        org_pk=__actor.org_id,
        by=__actor.uuid,
        time=time,
    )
    TimelineEventRepository(EventStore()).save(event, by=__actor)
    return event


@use_case
def update_timeline_event(
    __actor: RlcUser,
    uuid: UUID,
    text: str | None,
    time: datetime | None,
    folder_uuid: UUID,
):
    folder = folder_from_uuid(__actor, folder_uuid)
    event = TimelineEventRepository(EventStore()).load(
        uuid=uuid, by=__actor, folder=folder
    )
    e = TimelineEvent.InformationUpdated(
        text=text, by=__actor.uuid, uuid=uuid, time=time
    )
    event.apply(e)
    TimelineEventRepository(EventStore()).save(event, by=__actor)
    return event


@use_case
def delete_timeline_event(__actor: RlcUser, uuid: UUID, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)
    event = TimelineEventRepository(EventStore()).load(
        uuid=uuid, by=__actor, folder=folder
    )
    e = TimelineEvent.Deleted(by=__actor.uuid, uuid=uuid)
    event.apply(e)
    TimelineEventRepository(EventStore()).save(event, by=__actor)
    return event
