from uuid import UUID

from pydantic import AnyUrl

from core.auth.models.org_user import OrgUser
from core.org.models.org import ExternalLink
from core.seedwork.use_case_layer import UseCaseInputError, use_case

MAX_EXTERNAL_LINK_LENGTH = 4096


@use_case
def create_link(__actor: OrgUser, name: str, link: AnyUrl, order: int):
    _link: str = str(link)
    if len(_link) > MAX_EXTERNAL_LINK_LENGTH:
        raise UseCaseInputError(
            {
                "link": [
                    f"The link must be {MAX_EXTERNAL_LINK_LENGTH:,} characters or fewer."
                ]
            }
        )
    ExternalLink.objects.create(org=__actor.org, name=name, link=_link, order=order)


@use_case
def delete_link(__actor: OrgUser, id: UUID):
    ExternalLink.objects.filter(org=__actor.org, id=id).delete()
