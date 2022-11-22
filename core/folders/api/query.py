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

    return {"tree": tree.__dict__(), "available_persons": available_persons}
