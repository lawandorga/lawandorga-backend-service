import mimetypes

from django.http import FileResponse
from django.shortcuts import get_object_or_404

from core.auth.models import RlcUser
from core.seedwork.api_layer import Router

from ..models import UploadLink
from . import schemas

router = Router()


@router.get(
    url="<uuid:link>/",
    input_schema=schemas.InputQueryLink,
    output_schema=schemas.OutputQueryLink,
)
def query__link(rlc_user: RlcUser, data: schemas.InputQueryLink):
    pass


@router.get(
    url="<uuid:link>/<uuid:file>/",
    input_schema=schemas.InputDownloadFile,
    output_schema=FileResponse,
)
def query__download_file(rlc_user: RlcUser, data: schemas.InputDownloadFile):
    link = get_object_or_404(UploadLink, org_id=rlc_user.org_id, uuid=data.link)

    f = link.download(data.file, rlc_user)

    response = FileResponse(
        f, filename=f.name, content_type=mimetypes.guess_type(f.name)[0]
    )
    response["Content-Disposition"] = 'attachment; filename="{}"'.format(f.name)
    return response
