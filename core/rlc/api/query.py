from core.auth.models import RlcUser
from core.rlc.models import Group, Note
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get(
    url="group/<int:id>/",
    output_schema=schemas.OutputSingleGroup,
)
def query__get_group(rlc_user: RlcUser, data: schemas.InputQueryGroup):
    group = Group.objects.get(from_rlc__id=rlc_user.org_id, id=data.id)
    return {
        "id": group.pk,
        "name": group.name,
        "description": group.description,
        "members": list(group.members.all()),
        "permissions": list(group.permissions.all()),
    }


@router.get(url="groups/", output_schema=list[schemas.OutputGroup])
def query__list_groups(rlc_user: RlcUser):
    groups = Group.objects.filter(from_rlc__id=rlc_user.org_id)
    return list(groups)


@router.get(url="notes/", output_schema=list[schemas.OutputNote])
def query__list_notes(rlc_user: RlcUser):
    notes = Note.objects.filter(rlc__id=rlc_user.org_id)
    return list(notes)
