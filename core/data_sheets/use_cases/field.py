from uuid import UUID

from django.conf import settings
from django.db.models import ProtectedError

from core.auth.models import RlcUser
from core.data_sheets.use_cases.finders import find_field_from_id
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def delete_field(__actor: RlcUser, field_uuid: UUID, force_delete: bool):
    field = find_field_from_id(__actor, field_uuid)

    if force_delete:
        field.get_entry_model().objects.filter(field=field).delete()

    try:
        field.delete()
    except ProtectedError:
        entries = (
            field.get_entry_model().objects.filter(field=field).select_related("record")
        )
        records = [e.record for e in entries]
        record_urls = [
            "{}/folders/{}/".format(settings.MAIN_FRONTEND_URL, record.folder_uuid)
            for record in records
        ]
        record_text = "\n".join(record_urls)
        raise UseCaseError(
            "This field has associated data from one or more records. "
            "Please empty this field in the following records:\n{}".format(record_text)
        )
