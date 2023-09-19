from datetime import datetime
from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.domain.repositiories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import use_case
from core.timeline.models.event import TimelineEvent
from core.timeline.repositories.event import EventRepository


@use_case
def create_event(
    __actor: RlcUser,
    title: str,
    text: str,
    time: datetime,
    folder_uuid: UUID,
    er: EventRepository,
    fr: FolderRepository,
):
    folder = folder_from_uuid(__actor, folder_uuid)
    event = TimelineEvent.create(
        title=title,
        text=text,
        folder=folder,
        user=__actor,
        time=time,
    )
    er.save_event(event, __actor, fr)
    return event


@use_case
def update_event(
    __actor: RlcUser,
    uuid: UUID,
    title: str | None,
    text: str | None,
    time: datetime | None,
    er: EventRepository,
    fr: FolderRepository,
):
    event = er.get_event(uuid=uuid, user=__actor, fr=fr)
    event.update(title=title, text=text, time=time)
    er.save_event(event, __actor, fr)
    return event


@use_case
def delete_event(__actor: RlcUser, uuid: UUID, fur: EventRepository) -> None:
    fur.delete_event(uuid=uuid, user=__actor)
