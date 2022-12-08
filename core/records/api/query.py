import itertools

from core.auth.models import RlcUser
from core.records.api import schemas
from core.records.models import Record, RecordTemplate
from core.seedwork.api_layer import Router

router = Router()


@router.get(output_schema=schemas.OutputRecordsPage)
def query__records_page(rlc_user: RlcUser):
    records_1 = list(
        Record.objects.filter(template__rlc_id=rlc_user.org_id)
        .prefetch_related(*Record.get_unencrypted_prefetch_related())
        .select_related("template")
    )

    # Record.set_folders(rlc_user.org_id)

    records_2 = list(
        map(
            lambda r: (
                {
                    "id": r.id,
                    "attributes": r.attributes,
                    "delete_requested": r.delete_requested,
                    "has_access": r.has_access(rlc_user),
                }
            ),
            records_1,
        )
    )

    columns_1 = list(
        RecordTemplate.objects.filter(rlc_id=rlc_user.org_id).values_list(
            "show", flat=True
        )
    )
    columns_2 = itertools.chain(*columns_1)
    columns_3 = list(dict.fromkeys(columns_2))

    return {"columns": columns_3, "records": records_2}
