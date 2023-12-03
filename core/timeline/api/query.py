from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import RlcUser
from core.folders.infrastructure.folder_repository import DjangoFolderRepository
from core.seedwork.api_layer import Router
from core.timeline.repositories.event import EventRepository
from core.timeline.repositories.follow_up import FollowUpRepository

router = Router()


class OutputTimelineEvent(BaseModel):
    uuid: UUID
    title: str
    text: str
    time: datetime
    type: Literal["follow_up", "event", "old"]
    is_done: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class InputTimelineList(BaseModel):
    folder_uuid: UUID


@router.get(
    "timeline/<uuid:folder_uuid>/",
    output_schema=list[OutputTimelineEvent],
)
def query_timeline(rlc_user: RlcUser, data: InputTimelineList):
    fr = DjangoFolderRepository()
    fur = FollowUpRepository()
    er = EventRepository()
    folder = fr.retrieve(rlc_user.org_id, data.folder_uuid)
    events = er.list_events(folder_uuid=folder.uuid, user=rlc_user, fr=fr)
    follow_ups = fur.list_follow_ups(folder_uuid=folder.uuid, user=rlc_user, fr=fr)

    def get_time(item: Any):
        time = getattr(item, "time", None)
        assert time and isinstance(time, datetime)
        return time.isoformat()

    items = sorted(
        [*follow_ups, *events],
        key=get_time,
        reverse=True,
    )

    return items
