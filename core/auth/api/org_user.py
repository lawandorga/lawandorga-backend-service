from datetime import datetime, timedelta
from typing import Any, List, Optional
from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from pydantic import BaseModel, ConfigDict

from core.auth.models import OrgUser
from core.auth.use_cases.org_user import confirm_email
from core.files.query import has_org_files
from core.permissions.models import HasPermission
from core.permissions.static import (
    PERMISSION_ADMIN_MANAGE_PERMISSIONS,
    PERMISSION_ADMIN_MANAGE_USERS,
)
from core.seedwork.api_layer import ApiError, Router

router = Router()


class InputConfirmEmail(BaseModel):
    id: int
    token: str


@router.post(url="<int:id>/confirm_email/<str:token>/")
def command__confirm_email(data: InputConfirmEmail):
    confirm_email(None, data.id, data.token)


class OutputOrgUserSmall(BaseModel):
    id: int
    user_id: int
    phone_number: Optional[str]
    name: str
    email: str
    accepted: bool
    email_confirmed: bool
    locked: bool
    is_active: bool
    last_login_month: Optional[str]

    model_config = ConfigDict(from_attributes=True)


@router.get(output_schema=list[OutputOrgUserSmall])
def list_org_users(org_user: OrgUser):
    org_users = OrgUser.objects.filter(org=org_user.org)
    return list(org_users)


class OutputPermission(BaseModel):
    id: int
    permission_name: str
    source: str
    group_name: str | None
    user_name: str | None
    group_id: int | None

    model_config = ConfigDict(from_attributes=True)


class OutputOrgUserOptional(BaseModel):
    id: int
    user_id: int
    birthday: Optional[Any] = None
    phone_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    locked: Optional[bool] = None
    locked_legal: Optional[bool] = None
    email_confirmed: Optional[bool] = None
    is_active: Optional[bool] = None
    accepted: Optional[bool] = None
    updated: Optional[datetime] = None
    note: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created: Optional[datetime] = None
    speciality_of_study: Optional[str] = None
    speciality_of_study_display: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OutputUser(BaseModel):
    user: OutputOrgUserOptional
    permissions: Optional[list[OutputPermission]]


class InputOrgUserGet(BaseModel):
    id: int


@router.get(
    url="<int:id>/",
    output_schema=OutputUser,
)
def retrieve(data: InputOrgUserGet, org_user: OrgUser):
    found_org_user = OrgUser.objects.filter(id=data.id).first()
    if found_org_user is None:
        raise ApiError("The user could not be found.")

    if found_org_user.org != org_user.org:
        raise ApiError("The user could not be found.")

    if found_org_user.pk != org_user.pk and not org_user.has_permission(
        PERMISSION_ADMIN_MANAGE_USERS
    ):
        found_org_user_ret: Any = OutputOrgUserSmall.model_validate(
            found_org_user
        ).model_dump()
    else:
        found_org_user_ret = found_org_user

    permissions: Optional[list[HasPermission]] = None
    if org_user.has_permission(PERMISSION_ADMIN_MANAGE_PERMISSIONS):
        queryset = HasPermission.objects.filter(
            Q(user__org=found_org_user.org)
            | Q(group_has_permission__org=found_org_user.org)
        )
        queryset = queryset.select_related("permission", "group_has_permission", "user")
        groups = found_org_user.groups.all()
        queryset = queryset.filter(
            Q(user=found_org_user) | Q(group_has_permission__in=groups)
        )
        permissions = list(queryset)

    return {"user": found_org_user_ret, "permissions": permissions}


class OutputOrgUser(BaseModel):
    id: int
    user_id: int
    birthday: Optional[Any]
    phone_number: Optional[str]
    street: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    locked: bool
    locked_legal: bool
    email_confirmed: bool
    is_active: bool
    accepted: bool
    updated: datetime
    note: Optional[str]
    name: str
    email: str
    created: datetime
    speciality_of_study: Optional[str]
    speciality_of_study_display: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class Link(BaseModel):
    id: UUID
    name: str
    link: str
    order: int

    model_config = ConfigDict(from_attributes=True)


class Org(BaseModel):
    id: int
    name: str
    links: list[Link]
    disable_files: bool = False

    model_config = ConfigDict(from_attributes=True)


class Badges(BaseModel):
    profiles: int
    record_deletion_requests: int
    record_permit_requests: int
    legal: int
    record: int


class OutputOrgUserData(BaseModel):
    user: OutputOrgUser
    rlc: Org
    badges: Badges
    permissions: List[str]
    settings: Optional[dict[str, Any]]


@router.get(url="data_self/", output_schema=OutputOrgUserData)
def query__data(org_user: OrgUser):
    data = {
        "user": org_user,
        "rlc": {
            "id": org_user.org.pk,
            "name": org_user.org.name,
            "links": org_user.org.links,
            "disable_files": not has_org_files(org_user.org),
        },
        "badges": org_user.badges,
        "permissions": org_user.get_permissions(),
        "settings": org_user.frontend_settings,
    }
    return data


class OutputDashboardMember(BaseModel):
    name: str
    id: int
    rlcuserid: int


@router.get("dashboard/", output_schema=None | list[OutputDashboardMember])
def members_information(org_user: OrgUser):
    if org_user.has_permission(PERMISSION_ADMIN_MANAGE_USERS):
        members_data = []
        users = OrgUser.objects.filter(
            org=org_user.org, created__gt=(timezone.now() - timedelta(days=14))
        )
        for org_user in list(users):
            if org_user.groups.all().count() == 0:
                members_data.append(
                    {
                        "name": org_user.user.name,
                        "id": org_user.user.pk,
                        "rlcuserid": org_user.pk,
                    }
                )
        return members_data
    return None
