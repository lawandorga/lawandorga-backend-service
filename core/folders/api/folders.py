from core.auth.models import RlcUser
from core.folders.api.schemas import InputFolderCreate, OutputFolderTree
from core.folders.use_cases.folder import create_folder, get_repository
from core.seedwork.api_layer import Router

router = Router()


@router.post(input_schema=InputFolderCreate)
def command__create_folder(data: InputFolderCreate, rlc_user: RlcUser):
    create_folder(rlc_user, data.name, data.parent)


@router.get(output_schema=OutputFolderTree)
def query__list_folders(rlc_user: RlcUser):
    r = get_repository()
    tree = r.tree(rlc_user.org_id)
    return tree.__dict__()
