from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.letterhead import Letterhead
from core.seedwork.use_case_layer import finder_function, use_case


@finder_function
def get_letterhead(a: OrgUser, v: UUID) -> Letterhead:
    return Letterhead.objects.get(uuid=v, org_id=a.org_id)


@use_case
def create_letterhead(
    __actor: OrgUser,
    name: str,
    description: str,
    address_line_1: str = "",
    address_line_2: str = "",
    address_line_3: str = "",
    address_line_4: str = "",
    address_line_5: str = "",
    text_right: str = "",
):
    lh = Letterhead.create(
        __actor,
        name,
        description,
        address_line_1,
        address_line_2,
        address_line_3,
        address_line_4,
        address_line_5,
        text_right,
    )
    lh.save()


@use_case
def update_letterhead(
    __actor: OrgUser,
    letterhead_uuid: UUID,
    name: str,
    description: str,
    address_line_1: str,
    address_line_2: str,
    address_line_3: str,
    address_line_4: str,
    address_line_5: str,
    text_right: str,
):
    lh = get_letterhead(__actor, letterhead_uuid)
    lh.update_meta(name, description)
    lh.update_text(
        address_line_1,
        address_line_2,
        address_line_3,
        address_line_4,
        address_line_5,
        text_right,
    )
    lh.save()


@use_case
def delete_letterhead(__actor: OrgUser, letterhead_uuid: UUID):
    lh = get_letterhead(__actor, letterhead_uuid)
    lh.delete()
