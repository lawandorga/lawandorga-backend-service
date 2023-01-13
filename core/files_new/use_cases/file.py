from uuid import UUID

from django.core.files.uploadedfile import UploadedFile

from core.auth.models import RlcUser
from core.files_new.models import EncryptedRecordDocument
from core.files_new.use_cases.finder import file_from_uuid
from core.folders.use_cases.finders import folder_from_uuid
from core.seedwork.use_case_layer import UseCaseError, use_case


@use_case
def upload_a_file(__actor: RlcUser, file: UploadedFile, folder_uuid: UUID):
    folder = folder_from_uuid(__actor, folder_uuid)

    if not folder.has_access(__actor):
        raise UseCaseError(
            "You can not upload a file into this folder, because you have no access to this folder."
        )

    f = EncryptedRecordDocument.create(file, folder, __actor)
    f.upload(file, __actor)
    f.save()


@use_case
def delete_a_file(__actor: RlcUser, file_uuid: UUID):
    file = file_from_uuid(__actor, file_uuid)
    file.delete_on_cloud()
    file.delete()
