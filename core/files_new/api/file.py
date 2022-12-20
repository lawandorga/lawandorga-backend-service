from django.core.files.uploadedfile import InMemoryUploadedFile
from core.auth.models import RlcUser
from core.files_new.use_cases.file import upload_a_file
from core.seedwork.api_layer import Router, ApiError
from . import schemas

router = Router()


@router.post(input_schema=schemas.InputUploadFile)
def command__upload_file(rlc_user: RlcUser, data: schemas.InputUploadFile):
    if not isinstance(data.file, InMemoryUploadedFile):
        raise ApiError({"file": ["You need to submit a file"]})

    upload_a_file(rlc_user, data.file, data.folder)
