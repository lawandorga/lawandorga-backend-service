from typing import List

from core.auth.models import RlcUser
from core.rlc.api import schemas
from core.rlc.models import ExternalLink
from core.rlc.use_cases.org import accept_member_to_org
from core.seedwork.api_layer import ApiError, Router

router = Router()


# list links
@router.get(url="links/", output_schema=List[schemas.OutputExternalLink])
def _list(rlc_user: RlcUser):
    links = ExternalLink.objects.filter(org=rlc_user.org)
    links_list = list(links)
    return links_list


# create link
@router.post(
    url="links/",
    input_schema=schemas.InputExternalLinkCreate,
    output_schema=schemas.OutputExternalLink,
)
def _create(data: schemas.InputExternalLinkCreate, rlc_user: RlcUser):
    link = ExternalLink.objects.create(org=rlc_user.org, **data.dict())
    return link


# delete link
@router.delete(url="links/<uuid:id>/", input_schema=schemas.InputExternalLinkDelete)
def _delete(data: schemas.InputExternalLinkDelete, rlc_user: RlcUser):
    link = ExternalLink.objects.filter(org=rlc_user.org, id=data.id).first()
    if link is None:
        raise ApiError(
            "The link you tried to delete could not be found.",
        )
    link.delete()


# accept member
@router.post(
    url="accept_member/",
    input_schema=schemas.InputAcceptMember,
)
def command__accept_member(data: schemas.InputAcceptMember, rlc_user: RlcUser):
    accept_member_to_org(rlc_user, data.user)
