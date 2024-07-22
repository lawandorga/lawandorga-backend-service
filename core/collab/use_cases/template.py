from uuid import UUID

from django.db import transaction

from core.auth.models.org_user import OrgUser
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
    print("we are in the use case")
    old_letterhead = template.letterhead
    if old_letterhead:
        print("the old letterhead has the name " +
              old_letterhead.address_line_1)
        old_letterhead.delete()
    else:
        print("there is no old letterhead")
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
def delete_template(__actor: OrgUser, template_uuid: UUID):
    template = get_template(__actor, template_uuid)
    template.delete()
