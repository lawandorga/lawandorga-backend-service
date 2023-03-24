from core.auth.models import RlcUser
from core.data_sheets.models import RecordTemplate
from core.data_sheets.use_cases.finders import template_from_id
from core.seedwork.use_case_layer import UseCaseError, use_case
from core.static import PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def create_template(__actor: RlcUser, name: str):
    template = RecordTemplate.create(name=name, org=__actor.org)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def update_template(
    __actor: RlcUser, template_id: int, template_name: str, template_show: list[str]
):
    template = template_from_id(__actor, template_id)
    template.update_name(template_name)
    template.update_show(template_show)
    template.save()


@use_case(permissions=[PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])
def delete_template(__actor: RlcUser, template_id: int):
    template = template_from_id(__actor, template_id)
    if template.records.exists():
        raise UseCaseError(
            "This template can not be deleted as there are records that depend on it."
        )
    template.delete()
