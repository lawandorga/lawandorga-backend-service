import mimetypes

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError

from core.seedwork.api_layer import ApiError, Router

from ...auth.models import RlcUser
from ..models import EncryptedRecordDocument
from . import schemas

router = Router()


@router.get(
    url="<uuid:uuid>/download/",
    input_schema=schemas.InputQueryFile,
    output_schema=FileResponse,
)
def query__download_file(rlc_user: RlcUser, data: schemas.InputQueryFile):
    f = get_object_or_404(
        EncryptedRecordDocument, org_id=rlc_user.org_id, uuid=data.uuid
    )
    assert f.folder is not None
    key = f.folder.get_decryption_key(requestor=rlc_user).get_key()
    try:
        file = f.download(key)
    except ParseError:
        raise ApiError(
            "The file could not be found on the server. "
            "Please delete it or contact it@law-orga.de "
            "to have it recovered."
        )
    response = FileResponse(file, content_type=mimetypes.guess_type(f.get_key())[0])
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(f.name)
    return response


@router.get(
    url="<uuid:uuid>/",
    input_schema=schemas.InputQueryFile,
    output_schema=schemas.OutputFile,
)
def query__retrieve_file(rlc_user: RlcUser, data: schemas.InputQueryFile):
    f = get_object_or_404(
        EncryptedRecordDocument, org_id=rlc_user.org_id, uuid=data.uuid
    )
    return f
