from core.auth.models.org_user import RlcUser
from core.seedwork.api_layer import Router
from core.timeline.use_cases import create_timeline_event, delete_timeline_event

from . import schemas

router = Router()


@router.post("")
def command__create_timeline_event(
    rlc_user: RlcUser, data: schemas.InputTimelineEventCreate
):
    create_timeline_event(rlc_user, data.text, data.folder_uuid)


@router.post("delete/")
def command__delete_timeline_event(
    rlc_user: RlcUser, data: schemas.InputTimelineEventDelete
):
    delete_timeline_event(rlc_user, data.uuid, data.folder_uuid)
