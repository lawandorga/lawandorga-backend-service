from core.files_new.models import EncryptedRecordDocument


def file_from_uuid(actor, v) -> EncryptedRecordDocument:
    return EncryptedRecordDocument.objects.get(uuid=v, org_id=actor.org_id)
