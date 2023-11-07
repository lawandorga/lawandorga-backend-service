from core.auth.models import RlcUser
from core.folders.use_cases.folder import correct_folder_keys_of_others
from core.seedwork.api_layer import Router

router = Router()


@router.post(url="optimize/")
def command__optimize_folders(rlc_user: RlcUser):
    correct_folder_keys_of_others(rlc_user)
