from core.auth.models.org_user import OrgUser
from core.data_sheets.use_cases.record import create_a_data_sheet_within_a_folder
from core.records.use_cases.record import create_record
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post(output_schema=schemas.OutputCreateRecord)
def command__create_record(rlc_user: OrgUser, data: schemas.InputCreateRecord):
    folder_uuid = create_record(rlc_user, data.token)
    if data.template is not None:
        record = create_a_data_sheet_within_a_folder(
            rlc_user, data.token, folder_uuid, data.template
        )
        return {"folder_uuid": folder_uuid, "record_uuid": record.uuid}
    return {"folder_uuid": folder_uuid}
