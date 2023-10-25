from core.auth.models import RlcUser
from core.data_sheets.api import schemas
from core.data_sheets.models import DataSheet
from core.data_sheets.use_cases.access_delivery import (
    deliver_access_to_users_who_should_have_access,
)
from core.data_sheets.use_cases.record import create_a_data_sheet_within_a_folder
from core.seedwork.api_layer import Router

router = Router()


@router.post(
    url="within_folder/",
    output_schema=schemas.OutputRecordCreate,
)
def command__create_record_within_folder(
    rlc_user: RlcUser, data: schemas.InputRecordCreateWithinFolder
):
    record_uuid = create_a_data_sheet_within_a_folder(
        rlc_user, data.name, folder_uuid=data.folder, template_id=data.template
    )
    record = DataSheet.objects.get(uuid=record_uuid)
    return {"id": record.pk, "uuid": record.uuid, "folder_uuid": record.folder_uuid}


@router.post(url="optimize/")
def command__records_optimize(rlc_user: RlcUser):
    deliver_access_to_users_who_should_have_access(rlc_user)
