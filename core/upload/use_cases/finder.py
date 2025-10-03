from uuid import UUID

from core.auth.models import OrgUser
from core.seedwork.use_case_layer import finder_function
from core.upload.models import UploadLink


@finder_function
def link_from_uuid(actor: OrgUser, uuid: UUID) -> UploadLink:
    return UploadLink.objects.get(org_id=actor.org_id, uuid=uuid)


@finder_function
def link_from_uuid_dangerous(uuid: UUID) -> UploadLink:
    return UploadLink.objects.get(uuid=uuid)


@finder_function
def file_from_uuid(actor: OrgUser, uuid: UUID):
    return UploadLink.objects.get(files__uuid=uuid, org_id=actor.org_id).files.get(
        uuid=uuid
    )
