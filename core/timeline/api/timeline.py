from core.auth.models.org_user import RlcUser
from core.seedwork.api_layer import Router
from core.timeline.use_cases import (
    create_timeline_event,
    delete_timeline_event,
    update_timeline_event,
)

from . import schemas

router = Router()


@router.post("")
def command__create_timeline_event(
    rlc_user: RlcUser, data: schemas.InputTimelineEventCreate
):
    create_timeline_event(
        rlc_user,
        title=data.title,
        text=data.text,
        time=data.time,
        folder_uuid=data.folder_uuid,
    )


@router.post("update/")
def command__update_timeline_event(
    rlc_user: RlcUser, data: schemas.InputTimelineEventUpdate
):
    update_timeline_event(
        rlc_user,
        uuid=data.uuid,
        title=data.title,
        text=data.text,
        time=data.time,
        folder_uuid=data.folder_uuid,
    )


@router.post("delete/")
def command__delete_timeline_event(
    rlc_user: RlcUser, data: schemas.InputTimelineEventDelete
):
    delete_timeline_event(rlc_user, uuid=data.uuid, folder_uuid=data.folder_uuid)
