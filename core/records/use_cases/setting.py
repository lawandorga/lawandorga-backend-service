from uuid import UUID

from core.auth.models.org_user import OrgUser
from core.permissions.static import PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES
from core.records.models.setting import RecordsView
from core.records.use_cases.finders import find_view_by_uuid
from core.seedwork.use_case_layer import UseCaseError, check_permissions, use_case


@use_case
def create_view(
    __actor: OrgUser,
    name: str,
    columns: list[str],
    shared: bool = False,
    ordering: int = 0,
):
    if shared:
        check_permissions(
            __actor,
            [PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES],
            message_addition="You can only create views that are not shared.",
        )
    if len(columns) == 0:
        raise UseCaseError("Columns can not be empty.")
    for c in columns:
        if c == "":
            raise UseCaseError("Columns can not contain an empty column.")
    view = RecordsView.create(
        name=name, user=__actor, columns=columns, shared=shared, ordering=ordering
    )
    view.save()


@use_case
def update_view(
    __actor: OrgUser,
    uuid: UUID,
    name: str,
    columns: list[str],
    ordering: int,
    shared: bool = False,
):
    if len(columns) == 0:
        raise UseCaseError("Columns can not be empty.")
    for c in columns:
        if c == "":
            raise UseCaseError("Columns can not contain an empty column.")
    view = find_view_by_uuid(__actor, uuid)
    if view.shared:
        check_permissions(__actor, [PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES])

    view.update_information(name=name, columns=columns, ordering=ordering)
    if view.shared != shared:
        if shared:
            view.make_shared(__actor)
        else:
            view.make_private(__actor)

    view.save()


@use_case
def delete_view(__actor: OrgUser, uuid: UUID):
    view = find_view_by_uuid(__actor, uuid)
    if view.org is not None:
        check_permissions(
            __actor,
            [PERMISSION_ADMIN_MANAGE_RECORD_TEMPLATES],
        )
    view.delete()
