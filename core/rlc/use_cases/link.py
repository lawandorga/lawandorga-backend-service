from uuid import UUID

from pydantic import AnyUrl

from core.auth.models.org_user import OrgUser
from core.rlc.models.org import ExternalLink
from core.seedwork.use_case_layer import use_case


@use_case
def create_link(__actor: OrgUser, name: str, link: AnyUrl, order: int):
    _link: str = str(link)
    ExternalLink.objects.create(org=__actor.org, name=name, link=_link, order=order)


@use_case
def delete_link(__actor: OrgUser, id: UUID):
    ExternalLink.objects.filter(org=__actor.org, id=id).delete()
