from pydantic import BaseModel

from core.auth.models import OrgUser
from core.permissions.use_cases.has_permission import (
    create_has_permission,
    delete_has_permission,
)
from core.seedwork.api_layer import Router

router = Router()


class InputHasPermissionCreate(BaseModel):
    permission_id: int
    group_id: int | None = None
    user_id: int | None = None


@router.post()
def command__create_has_permission(rlc_user: OrgUser, data: InputHasPermissionCreate):
    create_has_permission(rlc_user, data.user_id, data.group_id, data.permission_id)


class InputHasPermissionDelete(BaseModel):
    has_permission_id: int


@router.delete("<int:has_permission_id>/")
def command__delete_has_permission(rlc_user: OrgUser, data: InputHasPermissionDelete):
    delete_has_permission(rlc_user, data.has_permission_id)
