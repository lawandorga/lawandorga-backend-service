from core.auth.models.org_user import OrgUser
from core.data_sheets.use_cases.sheet import create_a_data_sheet_within_a_folder
from core.records.use_cases.record import create_record_and_folder
from core.seedwork.api_layer import Router

from . import schemas

router = Router()


@router.post(output_schema=schemas.OutputCreateRecord)
def command__create_record(org_user: OrgUser, data: schemas.InputCreateRecord):
    folder_uuid = create_record_and_folder(org_user, data.token)
    if data.template is not None:
        sheet = create_a_data_sheet_within_a_folder(
            org_user, data.token, folder_uuid, data.template
        )
        return {"folder_uuid": folder_uuid, "record_uuid": sheet.uuid}
    return {"folder_uuid": folder_uuid}
