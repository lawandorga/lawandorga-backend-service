from core.auth.models import RlcUser
from core.records.api import schemas
from core.records.use_cases.record import create_a_record
from core.seedwork.api_layer import Router

router = Router()


@router.post(
    input_schema=schemas.InputRecordCreate, output_schema=schemas.OutputRecordCreate
)
def command__create_record(rlc_user: RlcUser, data: schemas.InputRecordCreate):
    record_pk = create_a_record(rlc_user, folder=data.folder, template=data.template)
    return {"id": record_pk}
