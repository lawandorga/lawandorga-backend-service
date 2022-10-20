from typing import List

from apps.core.auth.models import RlcUser
from apps.core.rlc.api import schemas
from apps.core.rlc.models import ExternalLink
from apps.static.api_layer import ApiError, Router

router = Router()


# list
@router.get(url="links/", output_schema=List[schemas.OutputExternalLink])
def _list(rlc_user: RlcUser):
    links = ExternalLink.objects.filter(org=rlc_user.org)
    links_list = list(links)
    return links_list


# create
@router.post(
    url="links/",
    input_schema=schemas.InputExternalLinkCreate,
    output_schema=schemas.OutputExternalLink,
)
def _create(data: schemas.InputExternalLinkCreate, rlc_user: RlcUser):
    link = ExternalLink.objects.create(org=rlc_user.org, **data.dict())
    return link


# delete
@router.delete(url="links/<uuid:id>/", input_schema=schemas.InputExternalLinkDelete)
def _delete(data: schemas.InputExternalLinkDelete, rlc_user: RlcUser):
    link = ExternalLink.objects.filter(org=rlc_user.org, id=data.id).first()
    if link is None:
        raise ApiError(
            "The link you tried to delete could not be found.",
        )
    link.delete()
