from django.db.models.query_utils import Q
from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import OrgUser
from core.permissions.models import HasPermission, Permission
from core.permissions.static import (
    get_all_admin_permissions,
    get_all_files_permissions,
    get_all_records_permissions,
)
from core.seedwork.api_layer import Router

router = Router()


class OutputPermission(BaseModel):
    id: int
    name: str
    description: str
    recommended_for: str

    model_config = ConfigDict(from_attributes=True)


class QueryPermissionsInput(BaseModel):
    user_id: int | None = None
    group_id: int | None = None


@router.get("permissions/", output_schema=list[OutputPermission])
def query__permissions(data: QueryPermissionsInput):
    all_permissions = Permission.objects.all()

    if data.user_id is not None or data.group_id is not None:
        q_filter = Q()
        if data.user_id is not None:
            q_filter |= Q(user_id=data.user_id)
        if data.group_id is not None:
            q_filter |= Q(group_has_permission_id=data.group_id)

        assigned_permissions = HasPermission.objects.filter(q_filter).values_list(
            "permission_id", flat=True
        )

        return list(all_permissions.exclude(id__in=assigned_permissions))

    return list(all_permissions)


class OutputHasPermission(BaseModel):
    id: int
    group_name: str | None
    user_name: str | None
    permission_name: str | None

    model_config = ConfigDict(from_attributes=True)


def get_has_permissions_of(
    org_user: OrgUser, permissions: list[str]
) -> list[HasPermission]:
    return list(
        HasPermission.objects.filter(
            permission__in=Permission.objects.filter(name__in=permissions)
        )
        .filter(
            Q(user__in=org_user.org.users.all())
            | Q(group_has_permission__in=org_user.org.groups.all())
        )
        .select_related("user", "group_has_permission", "permission")
    )


@router.get("has_permissions/record/", output_schema=list[OutputHasPermission])
def query__record_has_permissions(org_user: OrgUser):
    permissions = get_has_permissions_of(org_user, get_all_records_permissions())
    return permissions


@router.get("has_permissions/files/", output_schema=list[OutputHasPermission])
def query__files_has_permissions(org_user: OrgUser):
    permissions = get_has_permissions_of(org_user, get_all_files_permissions())
    return permissions


@router.get("has_permissions/admin/", output_schema=list[OutputHasPermission])
def query__admin_has_permissions(org_user: OrgUser):
    permissions = get_has_permissions_of(org_user, get_all_admin_permissions())
    return permissions
