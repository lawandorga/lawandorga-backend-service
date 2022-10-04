from typing import List

from apps.core.auth.models import RlcUser
from apps.static.api_layer import Router
from apps.static.service_layer import ServiceResult

from ..models import ExternalLink
from . import schemas

router = Router()

# list
LIST_SUCCESS = "User {} has successfully retrieved all external links."


@router.get(url="links/", output_schema=List[schemas.ExternalLink])
def _list(rlc_user: RlcUser):
    links = ExternalLink.objects.filter(org=rlc_user.org)
    links_list = list(links)
    return ServiceResult(LIST_SUCCESS, links_list)


# create
CREATE_SUCCESS = "User {} has successfully created an external link."


@router.post(
    url="links/",
    input_schema=schemas.ExternalLinkCreate,
    output_schema=schemas.ExternalLink,
)
def _create(data: schemas.ExternalLinkCreate, rlc_user: RlcUser):
    link = ExternalLink.objects.create(org=rlc_user.org, **data.dict())
    return ServiceResult(CREATE_SUCCESS, link)


# delete
DELETE_SUCCESS = "User {} has successfully deleted an external link."
DELETE_ERROR_NOT_FOUND = "User {} tried to delete an link that does not exist."


@router.delete(url="links/<uuid:id>/", input_schema=schemas.ExternalLinkDelete)
def _delete(data: schemas.ExternalLinkDelete, rlc_user: RlcUser):
    link = ExternalLink.objects.filter(org=rlc_user.org, id=data.id).first()
    if link is None:
        return ServiceResult(
            DELETE_ERROR_NOT_FOUND,
            error="The link you tried to delete could not be found.",
        )
    link.delete()
    return ServiceResult(DELETE_SUCCESS, {})
