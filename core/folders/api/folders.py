from core.auth.models import RlcUser
from core.folders.api import schemas
from core.folders.use_cases.folder import (
    correct_folder_keys_of_others,
    create_folder,
    delete_folder,
    grant_access,
    move_folder,
    rename_folder,
    revoke_access,
    toggle_inheritance,
)
from core.seedwork.api_layer import Router

router = Router()


@router.post(input_schema=schemas.InputFolderCreate)
def command__create_folder(data: schemas.InputFolderCreate, rlc_user: RlcUser):
    create_folder(rlc_user, data.name, data.parent)


@router.post(url="<uuid:id>/", input_schema=schemas.InputFolderUpdate)
def command__update_folder(data: schemas.InputFolderUpdate, rlc_user: RlcUser):
    rename_folder(rlc_user, data.name, data.id)


@router.post(url="<uuid:id>/grant_access/", input_schema=schemas.InputFolderAccess)
def command__grant_access_to_folder(data: schemas.InputFolderAccess, rlc_user: RlcUser):
    grant_access(rlc_user, data.user_uuid, data.id)


@router.post(url="<uuid:id>/revoke_access/", input_schema=schemas.InputFolderAccess)
def command__revoke_access_from_folder(
    data: schemas.InputFolderAccess, rlc_user: RlcUser
):
    revoke_access(rlc_user, data.user_uuid, data.id)


@router.delete(url="<uuid:id>/", input_schema=schemas.InputFolderDelete)
def command__delete_folder(data: schemas.InputFolderDelete, rlc_user: RlcUser):
    delete_folder(rlc_user, data.id)


@router.post(url="<uuid:folder>/move/", input_schema=schemas.InputFolderMove)
def command__move_folder(data: schemas.InputFolderMove, rlc_user: RlcUser):
    move_folder(rlc_user, data.folder, data.target)


@router.post(
    url="<uuid:folder>/toggle_inheritance/", input_schema=schemas.InputFolderToggleInheritance
)
def command__toggle_inheritance_of_folder(
    data: schemas.InputFolderToggleInheritance, rlc_user: RlcUser
):
    toggle_inheritance(rlc_user, data.folder)


@router.post(url="optimize/")
def command__optimize_folders(rlc_user: RlcUser):
    correct_folder_keys_of_others(rlc_user)
