from uuid import UUID

from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.rlc.models import ExternalLink, Group, Note
from core.seedwork.api_layer import Router


class OutputNote(BaseModel):
    id: int
    title: str
    note: str
    note_with_links: str

    model_config = ConfigDict(from_attributes=True)


class InputQueryGroup(BaseModel):
    id: int


class OutputGroup(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class OutputPermission(BaseModel):
    id: int
    permission_name: str

    model_config = ConfigDict(from_attributes=True)


class OutputMember(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class OutputSingleGroup(BaseModel):
    id: int
    name: str
    description: str | None
    permissions: list[OutputPermission]
    members: list[OutputMember]

    model_config = ConfigDict(from_attributes=True)


class OutputExternalLink(BaseModel):
    id: UUID
    name: str
    link: str
    order: int

    model_config = ConfigDict(from_attributes=True)


router = Router()


router = Router()


@router.get(url="links/", output_schema=list[OutputExternalLink])
def get_links(rlc_user: OrgUser):
    links = ExternalLink.objects.filter(org=rlc_user.org)
    links_list = list(links)
    return links_list


@router.get(
    url="group/<int:id>/",
    output_schema=OutputSingleGroup,
)
def query__get_group(rlc_user: OrgUser, data: InputQueryGroup):
    group = Group.objects.get(from_rlc__id=rlc_user.org_id, id=data.id)
    return {
        "id": group.pk,
        "name": group.name,
        "description": group.description,
        "members": list(group.members.all()),
        "permissions": list(group.permissions.all()),
    }


@router.get(url="groups/", output_schema=list[OutputGroup])
def query__list_groups(rlc_user: OrgUser):
    groups = Group.objects.filter(from_rlc__id=rlc_user.org_id)
    return list(groups)


@router.get(url="notes/", output_schema=list[OutputNote])
def query__list_notes(rlc_user: OrgUser):
    notes = Note.objects.filter(rlc__id=rlc_user.org_id)
    return list(notes)
