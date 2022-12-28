from django.core.files.uploadedfile import UploadedFile

from core.auth.models import RlcUser
from core.files_new.use_cases.file import delete_a_file, upload_a_file
from core.seedwork.api_layer import ApiError, Router

from . import schemas

router = Router()


@router.post(url="multiple/", input_schema=schemas.InputUploadMultipleFiles)
def command__upload_multiple_file(
    rlc_user: RlcUser, data: schemas.InputUploadMultipleFiles
):
    if data.files is None:
        raise ApiError({"files": ["No file was submitted."]})

    for file in data.files:
        if not isinstance(file, UploadedFile):
            raise ApiError(
                {"files": ["One of the files does not have the right format."]}
            )

    for file in data.files:
        upload_a_file(rlc_user, file, data.folder)


@router.post(input_schema=schemas.InputUploadFile)
def command__upload_file(rlc_user: RlcUser, data: schemas.InputUploadFile):
    if not isinstance(data.file, UploadedFile):
        raise ApiError({"file": ["You need to submit a file"]})

    upload_a_file(rlc_user, data.file, data.folder)


@router.delete(url="<uuid:uuid>/", input_schema=schemas.InputDeleteFile)
def command__delete_file(rlc_user: RlcUser, data: schemas.InputDeleteFile):
    delete_a_file(rlc_user, data.uuid)
