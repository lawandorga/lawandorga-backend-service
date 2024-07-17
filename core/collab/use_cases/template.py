from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.template import Template
from core.seedwork.use_case_layer import finder_function, use_case


@finder_function
def get_template(user: OrgUser, id: UUID) -> Template:
    return Template.objects.get(uuid=id, org_id=user.org_id)


@use_case
def create_template(
    __actor: OrgUser,
    name: str,
    description: str,
):
    template = Template.create(
        __actor,
        name,
        description,
    )
    template.save()


@use_case
def update_template(
    __actor: OrgUser,
    template_uuid: UUID,
    name: str,
):
    template = get_template(__actor, template_uuid)
    template.update_name(name)
    template.save()


@use_case
def update_description(
    __actor: OrgUser,
    template_uuid: UUID,
    description: str,
):
    template = get_template(__actor, template_uuid)
    template.update_description(description)
    template.save()

    # TODO: update letterhead?
    # TODO: update footer?


@use_case
def delete_template(__actor: OrgUser, template_uuid: UUID):
    template = get_template(__actor, template_uuid)
    template.delete()
