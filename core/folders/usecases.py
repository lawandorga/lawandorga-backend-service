from core.folders.use_cases.folder import (
    create_folder,
    delete_folder,
    grant_access,
    grant_access_to_group,
    move_folder,
    rename_folder,
    revoke_access,
    revoke_access_from_group,
    toggle_inheritance,
)

USECASES = {
    "folders/create_folder": create_folder,
    "folders/rename_folder": rename_folder,
    "folders/delete_folder": delete_folder,
    "folders/move_folder": move_folder,
    "folders/toggle_inheritance_folder": toggle_inheritance,
    "folders/grant_access_to_user": grant_access,
    "folders/revoke_access_from_user": revoke_access,
    "folders/grant_access_to_group": grant_access_to_group,
    "folders/revoke_access_from_group": revoke_access_from_group,
}
