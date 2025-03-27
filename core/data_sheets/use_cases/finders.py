from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import OrgUser
from core.data_sheets.models import DataSheet, DataSheetTemplate
from core.data_sheets.models.data_sheet import DataSheetEncryptedFileField
from core.data_sheets.models.template import RecordField
from core.records.models.record import RecordsRecord
from core.seedwork.use_case_layer import finder_function


@finder_function
def sheet_from_id(actor: OrgUser, v: int) -> DataSheet:
    return DataSheet.objects.get(id=v, template__org__id=actor.org_id)


@finder_function
def sheet_from_uuid(actor: OrgUser, v: UUID) -> DataSheet:
    return DataSheet.objects.get(uuid=v, template__org__id=actor.org_id)


@finder_function
def template_from_id(actor: OrgUser, v: int) -> DataSheetTemplate:
    return DataSheetTemplate.objects.get(id=v, org_id=actor.org_id)


@finder_function
def find_field_from_uuid(actor: OrgUser, uuid: UUID) -> RecordField:
    for subclass in RecordField.__subclasses__():
        try:
            return subclass.objects.get(uuid=uuid, template__org__id=actor.org_id)  # type: ignore
        except subclass.DoesNotExist:
            pass
    raise ObjectDoesNotExist()


@finder_function
def find_file_field_from_uuid(
    actor: OrgUser, uuid: UUID
) -> DataSheetEncryptedFileField:
    return DataSheetEncryptedFileField.objects.get(
        uuid=uuid, template__org__id=actor.org_id
    )


@finder_function
def find_field_from_id(actor: OrgUser, id: int) -> RecordField:
    raise Exception("fields with the same ids exist this does not work")


@finder_function
def find_record_from_folder_uuid(actor: OrgUser, v: UUID) -> RecordsRecord | None:
    return RecordsRecord.objects.filter(folder_uuid=v, org_id=actor.org_id).first()


@finder_function
def find_sheets_from_folder_uuid(actor: OrgUser, folder_uuid: UUID) -> list[DataSheet]:
    return list(
        DataSheet.objects.filter(
            folder_uuid=folder_uuid, template__org__id=actor.org_id
        )
    )
