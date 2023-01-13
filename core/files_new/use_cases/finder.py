from core.files_new.models import EncryptedRecordDocument
from core.seedwork.use_case_layer import finder_function


@finder_function
def file_from_uuid(actor, v) -> EncryptedRecordDocument:
    return EncryptedRecordDocument.objects.get(uuid=v, org_id=actor.org_id)
