from dataclasses import dataclass
from uuid import UUID

from django.db.models import Q

from core.auth.models import RlcUser
from core.data_sheets.api import schemas
from core.data_sheets.models import Record, RecordAccess, RecordDeletion, RecordTemplate
from core.data_sheets.use_cases.record import migrate_record_into_folder
from core.permissions.static import PERMISSION_RECORDS_ACCESS_ALL_RECORDS
from core.seedwork.api_layer import ApiError, Router

router = Router()


@dataclass
class SheetMigrate:
    sheet: Record
    current_user: RlcUser
    SHOW: bool

    @property
    def name(self) -> str:
        return self.sheet.name

    @property
    def uuid(self) -> UUID:
        return self.sheet.uuid

    @property
    def token(self) -> str:
        if "Token" in self.sheet.attributes:
            return str(self.sheet.attributes["Token"])
        return "-"

    @property
    def attributes(self) -> dict:
        if self.SHOW or self.current_user.uuid in map(
            lambda x: x["uuid"], self.persons_with_access
        ):
            return self.sheet.attributes
        return {}

    @property
    def persons_with_access(self) -> list:
        return [
            {"name": e.user.name, "uuid": e.user.uuid}
            for e in list(self.sheet.encryptions.all())
        ]


@router.get(url="non_migrated/", output_schema=list[schemas.OutputNonMigratedDataSheet])
def query__non_migrated(rlc_user: RlcUser):
    sheets_1 = list(
        Record.objects.filter(template__rlc_id=rlc_user.org_id)
        .filter(folder_uuid=None)
        .prefetch_related(*Record.UNENCRYPTED_PREFETCH_RELATED, "encryptions__user")
        .select_related("template")
    )

    show = rlc_user.has_permission(PERMISSION_RECORDS_ACCESS_ALL_RECORDS)

    sheets_2 = [
        SheetMigrate(sheet=s, current_user=rlc_user, SHOW=show) for s in sheets_1
    ]

    return sheets_2


@router.get(url="templates/", output_schema=list[schemas.OutputTemplate])
def query__templates(rlc_user: RlcUser):
    templates = RecordTemplate.objects.filter(rlc_id=rlc_user.org_id)
    return list(templates)


@router.get(
    url="templates/<int:id>/",
    output_schema=schemas.OutputTemplateDetail,
)
def query__template(rlc_user: RlcUser, data: schemas.InputTemplateDetail):
    return RecordTemplate.objects.get(rlc_id=rlc_user.org_id, id=data.id)


@router.get(
    url="<uuid:uuid>/",
    output_schema=schemas.OutputRecordDetail,
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
        migrate_record_into_folder(rlc_user, record)

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
        "template_name": record.template.name,
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
