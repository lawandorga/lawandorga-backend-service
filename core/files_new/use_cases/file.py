from django.core.files.uploadedfile import InMemoryUploadedFile

from core.auth.models import RlcUser
from core.files_new.models import EncryptedRecordDocument
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def upload_a_file(__actor: RlcUser, file: InMemoryUploadedFile, folder=find(folder_from_uuid)):
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not upload a file into this folder, because you have no access to this folder."
        )
    name = 'Unknown'
    if file.name:
        name = file.name
    f = EncryptedRecordDocument(name=name, folder_uuid=folder.uuid)
    f.save()
    f.upload(file, folder.get_encryption_key(requestor=__actor))
