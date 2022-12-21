import mimetypes

from django.http import FileResponse
from django.shortcuts import get_object_or_404

from core.seedwork.api_layer import Router

from ...auth.models import RlcUser
from ..models import EncryptedRecordDocument
from . import schemas

router = Router()


@router.get(
    url="<uuid:uuid>/download/", input_schema=schemas.InputQueryFile, output_schema=FileResponse
)
def query__file(rlc_user: RlcUser, data: schemas.InputQueryFile):
    f = get_object_or_404(
        EncryptedRecordDocument, org_id=rlc_user.org_id, uuid=data.uuid
    )
    assert f.folder is not None
    key = f.folder.get_decryption_key(requestor=rlc_user).get_key()
    file = f.download(key)
    response = FileResponse(file, content_type=mimetypes.guess_type(f.get_key())[0])
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(f.name)
    return response


@router.get(
    url="<uuid:uuid>/", input_schema=schemas.InputQueryFile, output_schema=FileResponse
)
def query__file(rlc_user: RlcUser, data: schemas.InputQueryFile):
    f = get_object_or_404(
        EncryptedRecordDocument, org_id=rlc_user.org_id, uuid=data.uuid
    )
    assert f.folder is not None
    key = f.folder.get_decryption_key(requestor=rlc_user).get_key()
    file = f.download(key)
    response = FileResponse(file, content_type=mimetypes.guess_type(f.get_key())[0])
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(f.name)
    return response
