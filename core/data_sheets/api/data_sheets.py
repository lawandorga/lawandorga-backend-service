from core.auth.models import OrgUser
from core.data_sheets.api import schemas
from core.data_sheets.models import DataSheet
from core.data_sheets.use_cases.access_delivery import (
    deliver_access_to_users_who_should_have_access,
)
from core.data_sheets.use_cases.sheet import create_a_data_sheet_within_a_folder
from core.seedwork.api_layer import Router

router = Router()


@router.post(
    url="within_folder/",
    output_schema=schemas.OutputRecordCreate,
)
def command__create_record_within_folder(
    org_user: OrgUser, data: schemas.InputRecordCreateWithinFolder
):
    record = create_a_data_sheet_within_a_folder(
        org_user, data.name, folder_uuid=data.folder, template_id=data.template
    )
    record = DataSheet.objects.get(uuid=record.uuid)
    return {"id": record.pk, "uuid": record.uuid, "folder_uuid": record.folder_uuid}


@router.post(url="optimize/")
def command__records_optimize(org_user: OrgUser):
    deliver_access_to_users_who_should_have_access(org_user)
