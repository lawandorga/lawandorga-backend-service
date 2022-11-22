from core.auth.models import RlcUser
from core.folders.api import schemas
from core.folders.use_cases.folder import (
    create_folder,
    delete_folder,
    get_repository,
    grant_access,
    rename_folder,
    revoke_access,
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
    grant_access(rlc_user, data.user_slug, data.id)


@router.post(url="<uuid:id>/revoke_access/", input_schema=schemas.InputFolderAccess)
def command__revoke_access_from_folder(
    data: schemas.InputFolderAccess, rlc_user: RlcUser
):
    revoke_access(rlc_user, data.user_slug, data.id)


@router.delete(url="<uuid:id>/", input_schema=schemas.InputFolderDelete)
def command__delete_folder(data: schemas.InputFolderDelete, rlc_user: RlcUser):
    delete_folder(rlc_user, data.id)


@router.get(output_schema=schemas.OutputFolderPage)
def query__list_folders(rlc_user: RlcUser):
    r = get_repository()
    tree = r.tree(rlc_user.org_id)
    return tree.__dict__()
