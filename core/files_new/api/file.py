from django.core.files.uploadedfile import InMemoryUploadedFile

from core.auth.models import RlcUser
from core.files_new.use_cases.file import delete_a_file, upload_a_file
from core.seedwork.api_layer import ApiError, Router

from . import schemas

router = Router()


@router.post(input_schema=schemas.InputUploadFile)
def command__upload_file(rlc_user: RlcUser, data: schemas.InputUploadFile):
    raise ApiError('File creation is disabled at the moment. It will be enabled again at about 2pm 22. Dec 2022.')

    # if not isinstance(data.file, InMemoryUploadedFile):
    #     raise ApiError({"file": ["You need to submit a file"]})
    #
    # upload_a_file(rlc_user, data.file, data.folder)


@router.delete(url="<uuid:uuid>/", input_schema=schemas.InputDeleteFile)
def command__delete_file(rlc_user: RlcUser, data: schemas.InputDeleteFile):
    delete_a_file(rlc_user, data.uuid)
