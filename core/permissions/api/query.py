from django.db.models.query_utils import Q
from pydantic import BaseModel, ConfigDict

from core.auth.models.org_user import OrgUser
from core.permissions.models import HasPermission, Permission
from core.permissions.static import (
    get_all_admin_permissions,
    get_all_collab_permissions,
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


@router.get("permissions/", output_schema=list[OutputPermission])
def query__permissions():
    return list(Permission.objects.all())


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
            | Q(group_has_permission__in=org_user.org.group_from_rlc.all())
        )
        .select_related("user", "group_has_permission", "permission")
    )


@router.get("has_permissions/collab/", output_schema=list[OutputHasPermission])
def query__collab_has_permissions(rlc_user: OrgUser):
    permissions = get_has_permissions_of(rlc_user, get_all_collab_permissions())
    return permissions


@router.get("has_permissions/record/", output_schema=list[OutputHasPermission])
def query__record_has_permissions(rlc_user: OrgUser):
    permissions = get_has_permissions_of(rlc_user, get_all_records_permissions())
    return permissions


@router.get("has_permissions/files/", output_schema=list[OutputHasPermission])
def query__files_has_permissions(rlc_user: OrgUser):
    permissions = get_has_permissions_of(rlc_user, get_all_files_permissions())
    return permissions


@router.get("has_permissions/admin/", output_schema=list[OutputHasPermission])
def query__admin_has_permissions(rlc_user: OrgUser):
    permissions = get_has_permissions_of(rlc_user, get_all_admin_permissions())
    return permissions
