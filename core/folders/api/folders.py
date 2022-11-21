from core.auth.models import RlcUser
from core.folders.api import schemas
from core.folders.use_cases.folder import (
    create_folder,
    delete_folder,
    get_repository,
    rename_folder,
)
from core.seedwork.api_layer import Router

router = Router()


@router.post(input_schema=schemas.InputFolderCreate)
def command__create_folder(data: schemas.InputFolderCreate, rlc_user: RlcUser):
    create_folder(rlc_user, data.name, data.parent)


@router.post(url="<uuid:id>/", input_schema=schemas.InputFolderUpdate)
def command__update_folder(data: schemas.InputFolderUpdate, rlc_user: RlcUser):
    rename_folder(rlc_user, data.name, data.id)


@router.delete(url="<uuid:id>/", input_schema=schemas.InputFolderDelete)
def command__delete_folder(data: schemas.InputFolderDelete, rlc_user: RlcUser):
    delete_folder(rlc_user, data.id)


@router.get(output_schema=schemas.OutputFolderTree)
def query__list_folders(rlc_user: RlcUser):
    r = get_repository()
    tree = r.tree(rlc_user.org_id)
    return tree.__dict__()
