import itertools

from django.db.models import Q

from core.auth.models import RlcUser
from core.records.api import schemas
from core.records.models import Record, RecordAccess, RecordDeletion, RecordTemplate
from core.seedwork.api_layer import ApiError, Router

router = Router()


@router.get(url="templates/", output_schema=list[schemas.OutputTemplate])
def query__templates(rlc_user: RlcUser):
    templates = RecordTemplate.objects.filter(rlc_id=rlc_user.org_id)
    return list(templates)


@router.get(
    url="templates/<int:id>/",
    input_schema=schemas.InputTemplateDetail,
    output_schema=schemas.OutputTemplateDetail,
)
def query__template(rlc_user: RlcUser, data: schemas.InputTemplateDetail):
    return RecordTemplate.objects.get(rlc_id=rlc_user.org_id, id=data.id)


@router.get(output_schema=schemas.OutputRecordsPage)
def query__records_page(rlc_user: RlcUser):
    records_1 = list(
        Record.objects.filter(template__rlc_id=rlc_user.org_id)
        .prefetch_related(*Record.UNENCRYPTED_PREFETCH_RELATED)
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
        Record.objects.prefetch_related(*Record.ALL_PREFETCH_RELATED)
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
        "entries": record.get_entries(rlc_user),
    }


@router.get("deletions/", output_schema=list[schemas.OutputRecordDeletion])
def query__deletions(rlc_user: RlcUser):
    deletions_1 = RecordDeletion.objects.filter(
        Q(requestor__org_id=rlc_user.org_id)
        | Q(processor__org_id=rlc_user.org_id)
        | Q(record__template__rlc_id=rlc_user.org_id)
    )
    deletions_2 = list(deletions_1)
    return deletions_2


@router.get("accesses/", output_schema=list[schemas.OutputRecordAccess])
def query__accesses(rlc_user: RlcUser):
    deletions_1 = RecordAccess.objects.filter(
        Q(requestor__org_id=rlc_user.org_id)
        | Q(processor__org_id=rlc_user.org_id)
        | Q(record__template__rlc_id=rlc_user.org_id)
    )
    deletions_2 = list(deletions_1)
    return deletions_2
