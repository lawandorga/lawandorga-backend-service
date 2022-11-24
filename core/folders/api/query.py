from core.auth.models import RlcUser
from core.folders.api import schemas
from core.folders.use_cases.folder import get_repository
from core.seedwork.api_layer import Router

router = Router()


@router.get(output_schema=schemas.OutputFolderPage)
def query__list_folders(rlc_user: RlcUser):
    r = get_repository()
    tree = r.tree(rlc_user.org_id)

    available_persons = RlcUser.objects.filter(org_id=rlc_user.org_id)

    return {"tree": tree.as_dict(), "available_persons": available_persons}


@router.get(url="available_folders/", output_schema=list[schemas.OutputAvailableFolder])
def query__available_folders(rlc_user: RlcUser):
    r = get_repository()
    folders_1 = r.list(rlc_user.org_id)
    folders_2 = list(map(lambda f: {"id": f.pk, "name": f.name}, folders_1))
    return folders_2
