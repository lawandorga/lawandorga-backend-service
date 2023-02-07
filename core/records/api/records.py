from core.auth.models import RlcUser
from core.records.api import schemas
from core.records.models import Record
from core.records.use_cases.access_delivery import (
    deliver_access_to_users_who_should_have_access,
)
from core.records.use_cases.record import (
    change_record_name,
    create_a_record_and_a_folder,
    create_a_record_within_a_folder,
)
from core.seedwork.api_layer import Router

router = Router()


@router.post(output_schema=schemas.OutputRecordCreate)
def command__create_record(rlc_user: RlcUser, data: schemas.InputRecordCreate):
    record_pk = create_a_record_and_a_folder(rlc_user, data.name, data.template)
    record = Record.objects.get(pk=record_pk)
    return {"id": record.pk, "uuid": record.uuid, "folder_uuid": record.folder_uuid}


@router.post(
    url="within_folder/",
    output_schema=schemas.OutputRecordCreate,
)
def command__create_record_within_folder(
    rlc_user: RlcUser, data: schemas.InputRecordCreateWithinFolder
):
    record_pk = create_a_record_within_a_folder(
        rlc_user, data.name, folder_uuid=data.folder, template_id=data.template
    )
    record = Record.objects.get(pk=record_pk)
    return {"id": record.pk, "uuid": record.uuid, "folder_uuid": record.folder_uuid}


@router.post(url="<int:id>/change_name/")
def command__change_record_name(rlc_user: RlcUser, data: schemas.InputRecordChangeName):
    change_record_name(rlc_user, data.name, data.id)


@router.post(url="optimize/")
def command__records_optimize(rlc_user: RlcUser):
    deliver_access_to_users_who_should_have_access(rlc_user)
