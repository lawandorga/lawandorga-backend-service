from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.collab.models.footer import Footer
from core.collab.use_cases.template import get_template
from core.seedwork.use_case_layer import finder_function, use_case


@finder_function
def get_footer(user: OrgUser, id: UUID) -> Footer:
    return Footer.objects.get(uuid=id, org_id=user.org_id)


@use_case
def create_footer(
    __actor: OrgUser,
    template_uuid: UUID,
    column_1: str = "",
    column_2: str = "",
    column_3: str = "",
    column_4: str = "",
):
    template = get_template(__actor, template_uuid)
    footer = Footer.create(
        __actor.org_id,
        column_1,
        column_2,
        column_3,
        column_4,
    )
    footer.save()
    template.update_footer(footer)


@use_case
def update_footer(
    __actor: OrgUser,
    footer_uuid: UUID,
    column_1: str = "",
    column_2: str = "",
    column_3: str = "",
    column_4: str = "",
):
    footer = get_footer(__actor, footer_uuid)
    footer.update_text(
        column_1,
        column_2,
        column_3,
        column_4,
    )
    footer.save()


@use_case
def delete_footer(__actor: OrgUser, footer_uuid: UUID):
    footer = get_footer(__actor, footer_uuid)
    footer.delete()
