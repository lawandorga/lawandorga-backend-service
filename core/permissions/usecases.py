from core.permissions.use_cases.has_permission import (
    create_has_permission,
    delete_has_permission,
)

USECASES = {
    "permissions/create_has_permission": create_has_permission,
    "permissions/delete_has_permission": delete_has_permission,
}
