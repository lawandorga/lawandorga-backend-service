from core.auth.models import OrgUser
from core.rlc.use_cases.note import create_note, delete_note, update_note
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post()
def command__create_note(rlc_user: OrgUser, data: schemas.InputNoteCreate):
    create_note(rlc_user, data.title, data.note)


@router.put(url="<int:id>/")
def command__update_note(rlc_user: OrgUser, data: schemas.InputNoteUpdate):
    update_note(rlc_user, data.id, data.title, data.note)


@router.delete(url="<int:id>/")
def command__delete_note(rlc_user: OrgUser, data: schemas.InputNoteDelete):
    delete_note(rlc_user, data.id)
