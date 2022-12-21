from django.core.files.uploadedfile import InMemoryUploadedFile

from core.auth.models import RlcUser
from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.finder import file_from_uuid
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import UseCaseError, find, use_case


@use_case
def upload_a_file(
    __actor: RlcUser, file: InMemoryUploadedFile, folder=find(folder_from_uuid)
):
    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not upload a file into this folder, because you have no access to this folder."
        )
    name = "Unknown"
    if file.name:
        name = file.name
    f = EncryptedRecordDocument(folder_uuid=folder.uuid, org_id=__actor.org_id)
    f.set_name(name)
    f.save()
    f.upload(file, folder.get_encryption_key(requestor=__actor).get_key())


@use_case
def delete_a_file(__actor: RlcUser, file=find(file_from_uuid)):
    file.delete_on_cloud()
    file.delete()
