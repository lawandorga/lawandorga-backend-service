from core.auth.models import RlcUser
from core.rlc.models import Group
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.get(
    url="group/<int:id>/",
    input_schema=schemas.InputQueryGroup,
    output_schema=schemas.OutputSingleGroup,
)
def query__get_group(rlc_user: RlcUser, data: schemas.InputQueryGroup):
    group = Group.objects.get(from_rlc__id=rlc_user.org_id, id=data.id)
    return group


@router.get(url="groups/", output_schema=list[schemas.OutputGroup])
def query__list_groups(rlc_user: RlcUser):
    groups = Group.objects.filter(from_rlc__id=rlc_user.org_id)
    return list(groups)
