from core.auth.models import RlcUser
from core.rlc.models import Note
from core.rlc.use_cases.finders import note_from_id
from core.seedwork.use_case_layer import use_case
from core.static import PERMISSION_DASHBOARD_MANAGE_NOTES


@use_case(permissions=[PERMISSION_DASHBOARD_MANAGE_NOTES])
def create_note(actor: RlcUser, title: str, note: str):
    note_obj = Note.create(actor.org, title, note)
    note_obj.save()


@use_case(permissions=[PERMISSION_DASHBOARD_MANAGE_NOTES])
def update_note(
    actor: RlcUser, note_id: int, title: str | None = None, note: str | None = None
):
    note_obj = note_from_id(actor, note_id)
    note_obj.update_information(new_title=title, new_note=note)
    note_obj.save()


@use_case(permissions=[PERMISSION_DASHBOARD_MANAGE_NOTES])
def delete_note(actor: RlcUser, note_id: int):
    note = note_from_id(actor, note_id)
    note.delete()
