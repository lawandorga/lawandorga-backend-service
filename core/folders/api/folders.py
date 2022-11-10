from core.auth.models import RlcUser
from core.folders.api.schemas import (
    InputFolderCreate,
    InputFolderDelete,
    OutputFolderTree,
)
from core.folders.use_cases.folder import create_folder, delete_folder, get_repository
from core.seedwork.api_layer import Router

router = Router()


@router.post(input_schema=InputFolderCreate)
def command__create_folder(data: InputFolderCreate, rlc_user: RlcUser):
    create_folder(rlc_user, data.name, data.parent)


@router.delete(url="<uuid:id>/", input_schema=InputFolderDelete)
def command__delete_folder(data: InputFolderDelete, rlc_user: RlcUser):
    delete_folder(rlc_user, data.id)


@router.get(output_schema=OutputFolderTree)
def query__list_folders(rlc_user: RlcUser):
    r = get_repository()
    tree = r.tree(rlc_user.org_id)
    return tree.__dict__()
