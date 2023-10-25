from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from core.auth.models import RlcUser
from core.data_sheets.models import Record, RecordTemplate
from core.data_sheets.models.record import RecordEncryptedFileField
from core.data_sheets.models.template import RecordField
from core.seedwork.use_case_layer import finder_function


@finder_function
def record_from_id(actor: RlcUser, v: int) -> Record:
    return Record.objects.get(id=v, template__rlc__id=actor.org_id)


@finder_function
def record_from_uuid(actor: RlcUser, v: UUID) -> Record:
    return Record.objects.get(uuid=v, template__rlc__id=actor.org_id)


@finder_function
def template_from_id(actor: RlcUser, v: int) -> RecordTemplate:
    return RecordTemplate.objects.get(id=v, rlc_id=actor.org_id)


@finder_function
def find_field_from_uuid(actor: RlcUser, uuid: UUID) -> RecordField:
    for subclass in RecordField.__subclasses__():
        try:
            return subclass.objects.get(uuid=uuid, template__rlc_id=actor.org_id)  # type: ignore
        except subclass.DoesNotExist:
            pass
    raise ObjectDoesNotExist()


@finder_function
def find_file_field_from_uuid(actor: RlcUser, uuid: UUID) -> RecordEncryptedFileField:
    return RecordEncryptedFileField.objects.get(
        uuid=uuid, template__rlc_id=actor.org_id
    )


@finder_function
def find_field_from_id(actor: RlcUser, id: int) -> RecordField:
    raise Exception("fields with the same ids exist this does not work")
