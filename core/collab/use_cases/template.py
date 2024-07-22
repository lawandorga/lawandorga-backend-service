from uuid import UUID

from django.db import transaction

from core.auth.models.org_user import OrgUser
from core.collab.models.footer import Footer
from core.collab.models.letterhead import Letterhead
from core.collab.models.template import Template
from core.seedwork.use_case_layer import finder_function, use_case


@finder_function
def get_template(user: OrgUser, id: UUID) -> Template:
    return Template.objects.get(uuid=id, org_id=user.org_id)


@use_case
def create_template(__actor: OrgUser, name: str, description: str = ""):
    template = Template.create(
        __actor,
        name,
        description,
    )
    with transaction.atomic():
        template.save()


@use_case
def update_template_name(
    __actor: OrgUser,
    template_uuid: UUID,
    name: str,
):
    template = get_template(__actor, template_uuid)
    template.update_name(name)
    template.save()


@use_case
def update_template_description(
    __actor: OrgUser,
    template_uuid: UUID,
    description: str = "",
):
    template = get_template(__actor, template_uuid)
    template.update_description(description)
    template.save()


@use_case
def update_template_letterhead(
    __actor: OrgUser,
    template_uuid,
    address_line_1: str = "",
    address_line_2: str = "",
    address_line_3: str = "",
    address_line_4: str = "",
    address_line_5: str = "",
    text_right: str = "",
):
    template = get_template(__actor, template_uuid)
    old_letterhead = template.letterhead
    if old_letterhead:
        old_letterhead.delete()
    new_letterhead = Letterhead.create(
        __actor.org_id,
        address_line_1=address_line_1,
        address_line_2=address_line_2,
        address_line_3=address_line_3,
        address_line_4=address_line_4,
        address_line_5=address_line_5,
        text_right=text_right,
    )
    new_letterhead.save()
    template.update_letterhead(new_letterhead)


@use_case
def update_template_footer(
    __actor: OrgUser,
    template_uuid,
    column_1: str = "",
    column_2: str = "",
    column_3: str = "",
    column_4: str = "",
):
    template = get_template(__actor, template_uuid)
    old_footer = template.footer
    if old_footer:
        old_footer.delete()
    new_footer = Footer.create(
        __actor.org_id,
        column_1=column_1,
        column_2=column_2,
        column_3=column_3,
        column_4=column_4,
    )
    new_footer.save()
    template.update_footer(new_footer)


@use_case
def delete_template(__actor: OrgUser, template_uuid: UUID):
    template = get_template(__actor, template_uuid)
    template.delete()
