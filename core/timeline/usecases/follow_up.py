from datetime import datetime
from uuid import UUID

from core.auth.models.org_user import RlcUser
from core.folders.domain.repositories.folder import FolderRepository
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import use_case
from core.timeline.models.follow_up import TimelineFollowUp
from core.timeline.repositories.follow_up import FollowUpRepository


@use_case
def create_follow_up(
    __actor: RlcUser,
    title: str,
    text: str,
    time: datetime,
    folder_uuid: UUID,
    fur: FollowUpRepository,
    fr: FolderRepository,
):
    folder = folder_from_uuid(__actor, folder_uuid)
    follow_up = TimelineFollowUp.create(
        title=title,
        text=text,
        folder=folder,
        user=__actor,
        time=time,
    )
    fur.save_follow_up(follow_up, __actor, fr)
    return follow_up


@use_case
def update_follow_up(
    __actor: RlcUser,
    uuid: UUID,
    title: str | None,
    text: str | None,
    is_done: bool | None,
    time: datetime | None,
    fur: FollowUpRepository,
    fr: FolderRepository,
):
    follow_up = fur.get_follow_up(uuid=uuid, user=__actor, fr=fr)
    follow_up.update(title=title, text=text, time=time, is_done=is_done)
    fur.save_follow_up(follow_up, __actor, fr)
    return follow_up


@use_case
def delete_follow_up(__actor: RlcUser, uuid: UUID, fur: FollowUpRepository) -> None:
    fur.delete_follow_up(uuid=uuid, user=__actor)


@use_case
def set_follow_up_as_done(
    __actor: RlcUser, uuid: UUID, fur: FollowUpRepository, fr: FolderRepository
) -> None:
    follow_up = fur.get_follow_up(uuid=uuid, user=__actor, fr=fr)
    follow_up.set_done()
    fur.save_follow_up(follow_up, __actor, fr)
