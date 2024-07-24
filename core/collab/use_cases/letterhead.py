from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models.org_user import OrgUser
from core.collab.models.letterhead import Letterhead
from core.collab.use_cases.template import get_template
from core.seedwork.use_case_layer import finder_function, use_case


@finder_function
def get_letterhead(user: OrgUser, id: UUID) -> Letterhead:
    return Letterhead.objects.get(uuid=id, org_id=user.org_id)


@use_case
def create_letterhead(
    __actor: OrgUser,
    template_uuid: UUID,
    address_line_1: str = "",
    address_line_2: str = "",
    address_line_3: str = "",
    address_line_4: str = "",
    address_line_5: str = "",
    text_right: str = "",
    logo: UploadedFile | None = None,
):
    template = get_template(__actor, template_uuid)
    letterhead = Letterhead.create(
        __actor.org_id,
        address_line_1,
        address_line_2,
        address_line_3,
        address_line_4,
        address_line_5,
        text_right,
    )
    if logo:
        letterhead.update_logo(logo)
    letterhead.save()
    template.update_letterhead(letterhead)


@use_case
def update_letterhead(
    __actor: OrgUser,
    letterhead_uuid: UUID,
    address_line_1: str = "",
    address_line_2: str = "",
    address_line_3: str = "",
    address_line_4: str = "",
    address_line_5: str = "",
    text_right: str = "",
    logo: UploadedFile | None = None,
):
    letterhead = get_letterhead(__actor, letterhead_uuid)
    letterhead.update_letterhead(
        address_line_1,
        address_line_2,
        address_line_3,
        address_line_4,
        address_line_5,
        text_right,
    )
    if logo:
        letterhead.update_logo(logo)
    letterhead.save()


@use_case
def delete_letterhead(__actor: OrgUser, letterhead_uuid: UUID):
    letterhead = get_letterhead(__actor, letterhead_uuid)
    letterhead.delete()
