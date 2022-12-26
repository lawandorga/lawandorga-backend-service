import itertools

from core.auth.models import RlcUser
from core.records.api import schemas
from core.records.models import Record, RecordTemplate
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.get(output_schema=schemas.OutputRecordsPage)
def query__records_page(rlc_user: RlcUser):
    records_1 = list(
        Record.objects.filter(template__rlc_id=rlc_user.org_id)
        .prefetch_related(*Record.get_unencrypted_prefetch_related())
        .select_related("template")
    )

    records_2 = [
        {
            "id": r.id,
            "uuid": r.uuid,
            "folder_uuid": r.folder_uuid,
            "attributes": r.attributes,
            "delete_requested": r.delete_requested,
            "has_access": r.has_access(rlc_user),
        }
        for r in records_1
    ]

    columns_1 = list(
        RecordTemplate.objects.filter(rlc_id=rlc_user.org_id).values_list(
            "show", flat=True
        )
    )
    columns_2 = itertools.chain(*columns_1)
    columns_3 = list(dict.fromkeys(columns_2))

    return {"columns": columns_3, "records": records_2}


@router.get(
    url="<uuid:uuid>/",
    output_schema=schemas.OutputRecordDetail,
    input_schema=schemas.InputQueryRecord,
)
def query__record(rlc_user: RlcUser, data: schemas.InputQueryRecord):
    record = (
        Record.objects.prefetch_related(*Record.get_encrypted_prefetch_related())
        .select_related("old_client", "template")
        .filter(template__rlc_id=rlc_user.org_id)
        .get(uuid=data.uuid)
    )

    if not record.has_access(rlc_user):
        raise ApiError("You have no access to this folder.")

    if not record.folder_uuid:
        record.put_in_folder(rlc_user)

    client = None
    if record.old_client:
        client = record.old_client
        private_key_user = rlc_user.get_private_key()
        client.decrypt(
            private_key_rlc=rlc_user.org.get_private_key(
                user=rlc_user.user, private_key_user=private_key_user
            )
        )

    return {
        "id": record.pk,
        "name": record.name,
        "uuid": record.uuid,
        "folder_uuid": record.folder_uuid,
        "created": record.created,
        "updated": record.updated,
        "client": client,
        "fields": record.template.get_fields_new(),
        "entries": record.get_entries_new(rlc_user),
    }
